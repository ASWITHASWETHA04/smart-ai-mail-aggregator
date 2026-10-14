import time
from flask import Blueprint, request, jsonify, current_app, g
from ..extensions import limiter
from ..security.decorators import jwt_required
from ..services.email_generator import (
    validate_generation_input,
    generate_email_draft,
    AIError,
    SUPPORTED_CATEGORIES,
    SUPPORTED_TONES,
    SUPPORTED_LENGTHS,
    SUPPORTED_LANGUAGES,
)
from ..services.event_recorder import record_generation_event

email_bp = Blueprint("email", __name__, url_prefix="/api/email")


@email_bp.route("/options", methods=["GET"])
def get_generation_options():
    """Return catalog of supported email categories, tones, lengths, and languages."""
    return jsonify({
        "categories": list(SUPPORTED_CATEGORIES.values()),
        "tones": list(SUPPORTED_TONES.values()),
        "lengths": list(SUPPORTED_LENGTHS.values()),
        "languages": list(SUPPORTED_LANGUAGES.values()),
    }), 200


@email_bp.route("/generate", methods=["POST"])
@jwt_required
@limiter.limit("10 per minute")
def generate_email():
    """Generate structured email draft (subject and body) via authenticated OpenAI request."""
    if not request.is_json:
        return jsonify({
            "error": "Bad Request",
            "message": "Request Content-Type must be 'application/json'.",
        }), 400

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({
            "error": "Bad Request",
            "message": "Malformed JSON payload in request.",
        }), 400

    is_valid, error_msg, validated_input = validate_generation_input(data)
    if not is_valid:
        return jsonify({
            "error": "Bad Request",
            "message": error_msg,
        }), 400

    user_id = g.current_user.id if getattr(g, "current_user", None) else None
    api_key = current_app.config.get("OPENAI_API_KEY")
    model = current_app.config.get("OPENAI_MODEL", "gpt-4o-mini")
    timeout_seconds = current_app.config.get("OPENAI_TIMEOUT_SECONDS", 30)
    max_retries = current_app.config.get("OPENAI_MAX_RETRIES", 2)

    start_time = time.perf_counter()

    try:
        draft = generate_email_draft(
            validated_input=validated_input,
            api_key=api_key,
            model=model,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )
        duration_ms = int((time.perf_counter() - start_time) * 1000)

        # Record telemetry event for successful generation
        record_generation_event(
            user_id=user_id,
            category=draft["category"],
            tone=draft["tone"],
            language=draft["language"],
            length=draft["length"],
            status="success",
            duration_ms=duration_ms,
            usage=draft.get("usage"),
            error_code=None,
        )

        return jsonify({
            "message": "Email draft generated successfully.",
            "draft": draft,
        }), 200

    except AIError as e:
        duration_ms = int((time.perf_counter() - start_time) * 1000)

        # Record telemetry event for failed generation
        record_generation_event(
            user_id=user_id,
            category=validated_input["category"],
            tone=validated_input["tone"],
            language=validated_input["language"],
            length=validated_input["length"],
            status="failed",
            duration_ms=duration_ms,
            usage=None,
            error_code=e.__class__.__name__,
        )

        return jsonify({
            "error": e.__class__.__name__,
            "message": e.message,
        }), e.status_code

    except Exception as e:
        duration_ms = int((time.perf_counter() - start_time) * 1000)

        # Record telemetry event for unexpected server error
        record_generation_event(
            user_id=user_id,
            category=validated_input["category"],
            tone=validated_input["tone"],
            language=validated_input["language"],
            length=validated_input["length"],
            status="failed",
            duration_ms=duration_ms,
            usage=None,
            error_code="UnexpectedServerError",
        )

        current_app.logger.error("Unexpected error in email generation: %s", e)
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred during email generation.",
        }), 500

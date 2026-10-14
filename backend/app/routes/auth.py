from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, current_app, g
from ..extensions import db, limiter
from ..models.user import User
from ..security.validation import validate_registration_payload
from ..security.jwt_utils import create_access_token
from ..security.decorators import jwt_required, roles_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
@limiter.limit("10 per minute")
def register():
    """Register a new user account with validated credentials and hashed password."""
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

    is_valid, error_msg, validated_data = validate_registration_payload(data)
    if not is_valid:
        return jsonify({
            "error": "Bad Request",
            "message": error_msg,
        }), 400

    normalized_email = validated_data["email"]

    # Parameterized query checking if account exists
    existing_user = User.query.filter_by(email=normalized_email).first()
    if existing_user:
        return jsonify({
            "error": "Conflict",
            "message": "An account with this email address already exists.",
        }), 409

    # Create new user record (role strictly restricted to 'user')
    user = User(
        email=normalized_email,
        role="user",
    )
    user.set_password(validated_data["password"])

    try:
        db.session.add(user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({
            "error": "Internal Server Error",
            "message": "Could not complete registration. Please try again later.",
        }), 500

    return jsonify({
        "message": "User registered successfully.",
        "user": user.to_dict(),
    }), 201


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    """Authenticate credentials and issue a signed, time-limited JWT access token."""
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

    email = data.get("email")
    password = data.get("password")

    if not email or not password or not isinstance(email, str) or not isinstance(password, str):
        return jsonify({
            "error": "Bad Request",
            "message": "Both 'email' and 'password' are required strings.",
        }), 400

    normalized_email = email.strip().lower()

    # Query user safely via parameterized query
    user = User.query.filter_by(email=normalized_email).first()

    # Constant-time comparison or generic failure response to mitigate enumeration
    if not user or not user.check_password(password):
        return jsonify({
            "error": "Unauthorized",
            "message": "Invalid email or password.",
        }), 401

    # Update last login timestamp
    user.last_login_at = datetime.now(timezone.utc)
    db.session.commit()

    # Generate JWT
    expires_in_minutes = current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", 60)
    token = create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role,
        secret_key=current_app.config["JWT_SECRET_KEY"],
        expires_in_minutes=expires_in_minutes,
        algorithm=current_app.config.get("JWT_ALGORITHM", "HS256"),
    )

    return jsonify({
        "message": "Authentication successful.",
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": expires_in_minutes * 60,
        "user": user.to_dict(),
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required
def get_current_user_profile():
    """Protected identity endpoint returning authenticated user context."""
    return jsonify({
        "user": g.current_user.to_dict(),
    }), 200


@auth_bp.route("/admin-check", methods=["GET"])
@jwt_required
@roles_required("admin")
def admin_only_check():
    """Protected role verification endpoint demonstrating RBAC enforcement."""
    return jsonify({
        "message": "Admin authorization verified.",
        "user": g.current_user.to_dict(),
    }), 200

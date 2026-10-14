import logging
from typing import Any
from ..extensions import db
from ..models.generation_event import EmailGenerationEvent

logger = logging.getLogger(__name__)


def record_generation_event(
    user_id: str | None,
    category: str,
    tone: str,
    language: str,
    length: str,
    status: str,
    duration_ms: int | None = None,
    usage: dict[str, Any] | None = None,
    error_code: str | None = None,
) -> EmailGenerationEvent | None:
    """
    Safely record an email generation telemetry event to the database.
    
    STRICT PRIVACY ENFORCEMENT:
    - Never accepts or persists prompt text, generated email body, recipient info, or credentials.
    - Captures only validated parameters, operational latency, sanitized error codes, and token counts.
    
    RELIABILITY POLICY:
    - If database persistence fails, rolls back cleanly and returns None.
    - Does NOT crash the caller or abort an already successful generation response.
    """
    event_type = "generation_succeeded" if status == "success" else "generation_failed"

    # Validate and sanitize tokens (must be non-negative integers reported by provider)
    prompt_tokens = None
    completion_tokens = None
    total_tokens = None

    if usage and isinstance(usage, dict):
        pt = usage.get("prompt_tokens")
        ct = usage.get("completion_tokens")
        tt = usage.get("total_tokens")
        if isinstance(pt, int) and pt >= 0:
            prompt_tokens = pt
        if isinstance(ct, int) and ct >= 0:
            completion_tokens = ct
        if isinstance(tt, int) and tt >= 0:
            total_tokens = tt

    # Sanitize duration_ms
    sanitized_duration: int | None = None
    if duration_ms is not None and isinstance(duration_ms, (int, float)):
        sanitized_duration = max(0, int(duration_ms))

    # Sanitize error_code string length
    sanitized_error_code: str | None = None
    if error_code:
        sanitized_error_code = str(error_code)[:64]

    try:
        event = EmailGenerationEvent(
            user_id=user_id,
            event_type=event_type,
            category=str(category),
            tone=str(tone),
            language=str(language),
            length=str(length),
            status=status,
            duration_ms=sanitized_duration,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            error_code=sanitized_error_code,
        )
        db.session.add(event)
        db.session.commit()
        return event
    except Exception as exc:
        db.session.rollback()
        logger.warning("Failed to record generation telemetry event: %s", exc)
        return None

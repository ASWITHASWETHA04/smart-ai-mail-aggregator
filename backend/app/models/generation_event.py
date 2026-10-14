import uuid
from datetime import datetime, timezone
from ..extensions import db


class EmailGenerationEvent(db.Model):
    """
    Privacy-conscious audit and analytics model recording generation metadata.
    
    STRICT PRIVACY POLICY:
    - Never stores email subject, email body, prompt text, purpose, key points, or context.
    - Never stores recipient names, email addresses, or unanonymized personal information.
    - Never stores bearer tokens, passwords, or provider API keys.
    - Provider token counts are stored only when reported by the upstream API and validated.
    """
    __tablename__ = "email_generation_events"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    event_type = db.Column(db.String(64), nullable=False)  # 'generation_succeeded', 'generation_failed'
    category = db.Column(db.String(64), nullable=False, index=True)
    tone = db.Column(db.String(32), nullable=False)
    language = db.Column(db.String(32), nullable=False)
    length = db.Column(db.String(32), nullable=False)
    status = db.Column(db.String(32), nullable=False, index=True)  # 'success', 'failed'
    duration_ms = db.Column(db.Integer, nullable=True)
    prompt_tokens = db.Column(db.Integer, nullable=True)
    completion_tokens = db.Column(db.Integer, nullable=True)
    total_tokens = db.Column(db.Integer, nullable=True)
    error_code = db.Column(db.String(64), nullable=True)  # Sanitized error category identifier

    user = db.relationship("User", backref=db.backref("generation_events", lazy=True))

    def to_dict(self) -> dict:
        """Serialize event metadata safely without exposing user identifiers."""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "event_type": self.event_type,
            "category": self.category,
            "tone": self.tone,
            "language": self.language,
            "length": self.length,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "error_code": self.error_code,
        }

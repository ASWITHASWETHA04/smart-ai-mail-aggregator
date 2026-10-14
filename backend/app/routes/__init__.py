"""Routes package for SmartMail AI."""
from .health import health_bp
from .auth import auth_bp
from .email import email_bp

__all__ = ["health_bp", "auth_bp", "email_bp"]

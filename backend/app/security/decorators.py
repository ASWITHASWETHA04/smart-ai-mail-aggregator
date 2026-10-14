from functools import wraps
from flask import request, jsonify, current_app, g
from .jwt_utils import decode_access_token, TokenExpiredError, TokenInvalidError
from ..models.user import User
from ..extensions import db


def jwt_required(f):
    """Decorator to enforce valid JWT authentication on protected endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({
                "error": "Unauthorized",
                "message": "Authorization header is missing.",
            }), 401

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({
                "error": "Unauthorized",
                "message": "Authorization header must be formatted as 'Bearer <token>'.",
            }), 401

        token = parts[1]
        jwt_secret = current_app.config.get("JWT_SECRET_KEY")
        algorithm = current_app.config.get("JWT_ALGORITHM", "HS256")

        try:
            payload = decode_access_token(token, jwt_secret, algorithm=algorithm)
        except TokenExpiredError:
            return jsonify({
                "error": "Unauthorized",
                "message": "Access token has expired. Please log in again.",
            }), 401
        except TokenInvalidError:
            return jsonify({
                "error": "Unauthorized",
                "message": "Invalid or malformed access token.",
            }), 401

        user_id = payload.get("sub")
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({
                "error": "Unauthorized",
                "message": "User associated with this token no longer exists.",
            }), 401

        # Store authenticated user on Flask context
        g.current_user = user
        return f(*args, **kwargs)

    return decorated_function


def roles_required(*allowed_roles):
    """Decorator to enforce role-based access control (RBAC)."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = getattr(g, "current_user", None)
            if not current_user:
                return jsonify({
                    "error": "Unauthorized",
                    "message": "Authentication required before role verification.",
                }), 401

            if current_user.role not in allowed_roles:
                return jsonify({
                    "error": "Forbidden",
                    "message": "Access denied: insufficient permissions.",
                }), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator

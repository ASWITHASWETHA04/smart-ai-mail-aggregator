from datetime import datetime, timedelta, timezone
import jwt


class TokenSecurityError(Exception):
    """Base exception for token authentication failures."""
    pass


class TokenExpiredError(TokenSecurityError):
    """Raised when an access token has expired."""
    pass


class TokenInvalidError(TokenSecurityError):
    """Raised when an access token signature or payload is invalid/tampered."""
    pass


def create_access_token(
    user_id: str,
    email: str,
    role: str,
    secret_key: str,
    expires_in_minutes: int = 60,
    algorithm: str = "HS256",
) -> str:
    """Generate a cryptographically signed, time-limited JWT access token."""
    now = datetime.now(timezone.utc)
    expiration = now + timedelta(minutes=expires_in_minutes)

    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expiration.timestamp()),
    }

    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_access_token(
    token: str,
    secret_key: str,
    algorithm: str = "HS256",
) -> dict:
    """Verify signature and claims for a JWT token.
    
    Raises TokenExpiredError if expired.
    Raises TokenInvalidError if tampered, malformed, or missing required claims.
    """
    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[algorithm],
            options={"require": ["sub", "email", "role", "exp", "iat"]},
        )
        return payload
    except jwt.ExpiredSignatureError as e:
        raise TokenExpiredError("Access token has expired.") from e
    except jwt.InvalidTokenError as e:
        raise TokenInvalidError("Access token is invalid or has been tampered with.") from e

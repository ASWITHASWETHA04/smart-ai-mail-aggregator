import re
from email_validator import validate_email, EmailNotValidError

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
EMAIL_MAX_LENGTH = 255


def validate_and_normalize_email(email_raw: str) -> tuple[bool, str, str | None]:
    """Validate email format and return normalized lowercase email address."""
    if not isinstance(email_raw, str):
        return False, "", "Email must be a string."

    trimmed = email_raw.strip()
    if not trimmed:
        return False, "", "Email cannot be empty."

    if len(trimmed) > EMAIL_MAX_LENGTH:
        return False, "", f"Email exceeds maximum length of {EMAIL_MAX_LENGTH} characters."

    try:
        # Check email format without delivering or querying DNS in testing/offline
        validated = validate_email(trimmed, check_deliverability=False)
        return True, validated.normalized.lower(), None
    except EmailNotValidError as e:
        return False, "", f"Invalid email format: {str(e)}"


def validate_password_strength(password: str) -> tuple[bool, str | None]:
    """Enforce documented password security policy:
    - Between 8 and 128 characters.
    - Contains at least one letter.
    - Contains at least one number.
    """
    if not isinstance(password, str):
        return False, "Password must be a string."

    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters in length."

    if len(password) > PASSWORD_MAX_LENGTH:
        return False, f"Password exceeds maximum length of {PASSWORD_MAX_LENGTH} characters."

    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one letter."

    if not re.search(r"\d", password):
        return False, "Password must contain at least one numerical digit."

    return True, None


def validate_registration_payload(data: dict) -> tuple[bool, str | None, dict | None]:
    """Validate incoming registration request JSON data."""
    if not isinstance(data, dict):
        return False, "Request payload must be a JSON object.", None

    email_raw = data.get("email")
    password_raw = data.get("password")

    if not email_raw:
        return False, "Field 'email' is required.", None

    if not password_raw:
        return False, "Field 'password' is required.", None

    # Defense against privilege escalation through public self-assignment
    requested_role = data.get("role")
    if requested_role and requested_role.strip().lower() != "user":
        return False, "Public registration cannot assign privileged roles.", None

    # Validate email
    is_valid_email, normalized_email, email_err = validate_and_normalize_email(email_raw)
    if not is_valid_email:
        return False, email_err, None

    # Validate password
    is_valid_password, pass_err = validate_password_strength(password_raw)
    if not is_valid_password:
        return False, pass_err, None

    return True, None, {
        "email": normalized_email,
        "password": password_raw,
        "role": "user",
    }

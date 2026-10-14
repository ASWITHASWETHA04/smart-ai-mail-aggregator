import logging
import re

SENSITIVE_PATTERNS = [
    (re.compile(r"(bearer\s+)[a-zA-Z0-9\-_.]+", re.IGNORECASE), r"\1[REDACTED_TOKEN]"),
    (re.compile(r"('?password'?\s*[:=]\s*'?)[^',}\s]+('?)", re.IGNORECASE), r"\1[REDACTED_PASSWORD]\2"),
    (re.compile(r"('?secret'?\s*[:=]\s*'?)[^',}\s]+('?)", re.IGNORECASE), r"\1[REDACTED_SECRET]\2"),
    (re.compile(r"('?jwt_secret_key'?\s*[:=]\s*'?)[^',}\s]+('?)", re.IGNORECASE), r"\1[REDACTED_KEY]\2"),
    (re.compile(r"('?api_key'?\s*[:=]\s*'?)[^',}\s]+('?)", re.IGNORECASE), r"\1[REDACTED_API_KEY]\2"),
]


class SafeLogFilter(logging.Filter):
    """Logging filter that scrubs tokens, passwords, and secrets from all log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.redact(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: self.redact(str(v)) for k, v in record.args.items()}
            elif isinstance(record.args, (list, tuple)):
                record.args = tuple(self.redact(str(arg)) for arg in record.args)
        return True

    @staticmethod
    def redact(text: str) -> str:
        for pattern, replacement in SENSITIVE_PATTERNS:
            text = pattern.sub(replacement, text)
        return text

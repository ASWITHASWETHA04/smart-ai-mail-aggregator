"""Services package for SmartMail AI."""
from .email_generator import (
    generate_email_draft,
    validate_generation_input,
    AIError,
    AIServiceConfigurationError,
    AIProviderAuthenticationError,
    AIProviderRateLimitError,
    AIProviderTimeoutError,
    AIProviderConnectionError,
    AIParsingError,
    SUPPORTED_CATEGORIES,
    SUPPORTED_TONES,
    SUPPORTED_LENGTHS,
    SUPPORTED_LANGUAGES,
)

__all__ = [
    "generate_email_draft",
    "validate_generation_input",
    "AIError",
    "AIServiceConfigurationError",
    "AIProviderAuthenticationError",
    "AIProviderRateLimitError",
    "AIProviderTimeoutError",
    "AIProviderConnectionError",
    "AIParsingError",
    "SUPPORTED_CATEGORIES",
    "SUPPORTED_TONES",
    "SUPPORTED_LENGTHS",
    "SUPPORTED_LANGUAGES",
]

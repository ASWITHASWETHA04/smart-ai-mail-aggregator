import json
from unittest.mock import MagicMock, patch
import pytest
import openai
from app import create_app
from app.extensions import db
from app.models.user import User
from app.security.jwt_utils import create_access_token


@pytest.fixture
def app_instance():
    """Create isolated application instance with test config."""
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app_instance):
    return app_instance.test_client()


@pytest.fixture
def auth_headers(app_instance):
    """Generate authenticated user and valid bearer token."""
    with app_instance.app_context():
        user = User(email="academic@university.edu", role="user")
        user.set_password("SecurePassword1")
        db.session.add(user)
        db.session.commit()
        token = create_access_token(
            user.id,
            user.email,
            user.role,
            app_instance.config["JWT_SECRET_KEY"],
        )
        return {"Authorization": f"Bearer {token}"}


def test_email_options_endpoint(client):
    """Verify GET /api/email/options returns supported categories, tones, lengths, and languages."""
    response = client.get("/api/email/options")
    assert response.status_code == 200
    data = response.get_json()
    assert "categories" in data
    assert "tones" in data
    assert "lengths" in data
    assert "languages" in data
    assert "Academic communication" in data["categories"]
    assert "Formal" in data["tones"]
    assert "English" in data["languages"]
    assert "Medium" in data["lengths"]


def test_generate_requires_authentication(client):
    """Verify unauthenticated requests to POST /api/email/generate return 401."""
    payload = {
        "purpose": "Request feedback on research draft",
        "category": "Academic communication",
        "tone": "Formal",
    }
    response = client.post("/api/email/generate", json=payload)
    assert response.status_code == 401
    assert "Authorization header is missing" in response.get_json()["message"]


def test_generate_rejects_missing_purpose(client, auth_headers):
    """Verify validation rejects missing purpose field."""
    payload = {
        "category": "Academic communication",
        "tone": "Formal",
    }
    response = client.post("/api/email/generate", json=payload, headers=auth_headers)
    assert response.status_code == 400
    assert "purpose" in response.get_json()["message"]


def test_generate_rejects_purpose_too_short(client, auth_headers):
    """Verify validation rejects purpose shorter than 5 characters."""
    payload = {
        "purpose": "Hi",
        "category": "Academic communication",
        "tone": "Formal",
    }
    response = client.post("/api/email/generate", json=payload, headers=auth_headers)
    assert response.status_code == 400
    assert "at least 5 characters" in response.get_json()["message"]


def test_generate_rejects_invalid_category(client, auth_headers):
    """Verify validation rejects unsupported category."""
    payload = {
        "purpose": "Request meeting with advisor",
        "category": "Unsupported Random Category",
        "tone": "Formal",
    }
    response = client.post("/api/email/generate", json=payload, headers=auth_headers)
    assert response.status_code == 400
    assert "Invalid 'category'" in response.get_json()["message"]


def test_generate_rejects_invalid_tone(client, auth_headers):
    """Verify validation rejects unsupported tone."""
    payload = {
        "purpose": "Request meeting with advisor",
        "category": "Academic communication",
        "tone": "Aggressive",
    }
    response = client.post("/api/email/generate", json=payload, headers=auth_headers)
    assert response.status_code == 400
    assert "Invalid 'tone'" in response.get_json()["message"]


def test_generate_rejects_invalid_language(client, auth_headers):
    """Verify validation rejects unsupported language."""
    payload = {
        "purpose": "Request meeting with advisor",
        "category": "Academic communication",
        "tone": "Formal",
        "language": "Klingon",
    }
    response = client.post("/api/email/generate", json=payload, headers=auth_headers)
    assert response.status_code == 400
    assert "Invalid 'language'" in response.get_json()["message"]


def test_generate_rejects_invalid_length(client, auth_headers):
    """Verify validation rejects unsupported length."""
    payload = {
        "purpose": "Request meeting with advisor",
        "category": "Academic communication",
        "tone": "Formal",
        "length": "Gigantic",
    }
    response = client.post("/api/email/generate", json=payload, headers=auth_headers)
    assert response.status_code == 400
    assert "Invalid 'length'" in response.get_json()["message"]


def test_generate_rejects_excessive_input_lengths(client, auth_headers):
    """Verify validation enforces upper bounds on input fields."""
    payload = {
        "purpose": "x" * 1005,  # > 1000 limit
        "category": "Academic communication",
        "tone": "Formal",
    }
    response = client.post("/api/email/generate", json=payload, headers=auth_headers)
    assert response.status_code == 400
    assert "cannot exceed 1000 characters" in response.get_json()["message"]


def test_generate_fails_safe_when_api_key_missing(client, auth_headers, app_instance):
    """Verify missing OPENAI_API_KEY returns safe 503 Service Unavailable."""
    app_instance.config["OPENAI_API_KEY"] = None
    payload = {
        "purpose": "Request feedback on research paper",
        "category": "Academic communication",
        "tone": "Formal",
    }
    response = client.post("/api/email/generate", json=payload, headers=auth_headers)
    assert response.status_code == 503
    data = response.get_json()
    assert data["error"] == "AIServiceConfigurationError"
    assert "OPENAI_API_KEY" in data["message"]


def test_successful_mocked_generation(client, auth_headers):
    """Verify successful generation pipeline using mocked OpenAI client (test double)."""
    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps({
        "subject": "Research Paper Draft Feedback Request",
        "body": "Dear Dr. Smith,\n\nI hope this email finds you well. I have completed the draft of our paper and would appreciate your guidance.\n\nSincerely,\n[Your Name]",
    })
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.usage.prompt_tokens = 120
    mock_response.usage.completion_tokens = 85
    mock_response.usage.total_tokens = 205

    payload = {
        "purpose": "Request feedback on research paper draft",
        "category": "Academic communication",
        "tone": "Formal",
        "length": "Medium",
        "language": "English",
        "recipient": "Dr. Smith",
        "key_points": "Draft completed, feedback needed by Friday",
    }

    with patch("app.services.email_generator.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_cls.return_value = mock_client

        response = client.post("/api/email/generate", json=payload, headers=auth_headers)
        assert response.status_code == 200

        data = response.get_json()
        assert data["message"] == "Email draft generated successfully."
        draft = data["draft"]
        assert draft["subject"] == "Research Paper Draft Feedback Request"
        assert "Dear Dr. Smith" in draft["body"]
        assert draft["category"] == "Academic communication"
        assert draft["tone"] == "Formal"
        assert draft["length"] == "Medium"
        assert draft["language"] == "English"
        assert draft["model"] == "gpt-4o-mini"
        assert draft["usage"]["total_tokens"] == 205


def test_mocked_provider_auth_error_returns_502(client, auth_headers):
    """Verify upstream OpenAI authentication failure returns 502 Bad Gateway safely."""
    with patch("app.services.email_generator.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = openai.AuthenticationError(
            "Incorrect API key provided", response=MagicMock(status_code=401), body=None
        )
        mock_openai_cls.return_value = mock_client

        payload = {
            "purpose": "Follow up on internship application",
            "category": "Follow-up",
            "tone": "Professional",
        }
        response = client.post("/api/email/generate", json=payload, headers=auth_headers)
        assert response.status_code == 502
        data = response.get_json()
        assert data["error"] == "AIProviderAuthenticationError"
        assert "authentication failed" in data["message"].lower()


def test_mocked_provider_rate_limit_returns_429(client, auth_headers):
    """Verify upstream OpenAI rate limit returns 429 Too Many Requests."""
    with patch("app.services.email_generator.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = openai.RateLimitError(
            "Rate limit exceeded", response=MagicMock(status_code=429), body=None
        )
        mock_openai_cls.return_value = mock_client

        payload = {
            "purpose": "Follow up on internship application",
            "category": "Follow-up",
            "tone": "Professional",
        }
        response = client.post("/api/email/generate", json=payload, headers=auth_headers)
        assert response.status_code == 429
        data = response.get_json()
        assert data["error"] == "AIProviderRateLimitError"


def test_mocked_provider_timeout_returns_504(client, auth_headers):
    """Verify upstream timeout returns 504 Gateway Timeout."""
    with patch("app.services.email_generator.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = openai.APITimeoutError(request=MagicMock())
        mock_openai_cls.return_value = mock_client

        payload = {
            "purpose": "Follow up on internship application",
            "category": "Follow-up",
            "tone": "Professional",
        }
        response = client.post("/api/email/generate", json=payload, headers=auth_headers)
        assert response.status_code == 504
        data = response.get_json()
        assert data["error"] == "AIProviderTimeoutError"


def test_mocked_malformed_provider_output_returns_502(client, auth_headers):
    """Verify non-JSON or missing field provider responses return 502 AIParsingError."""
    mock_choice = MagicMock()
    mock_choice.message.content = "Not a json response string"
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.usage = None

    with patch("app.services.email_generator.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_cls.return_value = mock_client

        payload = {
            "purpose": "Follow up on internship application",
            "category": "Follow-up",
            "tone": "Professional",
        }
        response = client.post("/api/email/generate", json=payload, headers=auth_headers)
        assert response.status_code == 502
        data = response.get_json()
        assert data["error"] == "AIParsingError"


def test_generation_endpoint_rate_limiting(client, auth_headers):
    """Verify that exceeding the 10 per minute rate limit returns HTTP 429."""
    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps({"subject": "Test", "body": "Test body"})
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.usage = None

    payload = {
        "purpose": "Follow up on internship application",
        "category": "Follow-up",
        "tone": "Professional",
    }

    with patch("app.services.email_generator.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_cls.return_value = mock_client

        # Send 10 requests (all allowed)
        for _ in range(10):
            res = client.post("/api/email/generate", json=payload, headers=auth_headers)
            assert res.status_code == 200

        # 11th request exceeds limit
        blocked = client.post("/api/email/generate", json=payload, headers=auth_headers)
        assert blocked.status_code == 429
        assert blocked.get_json()["error"] == "Rate limit exceeded"

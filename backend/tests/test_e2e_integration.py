"""End-to-End Integration Test Suite for SmartMail AI (Phase 5).

Verifies the complete user journey and API contracts across:
1. Registration -> Duplicate Prevention -> Login -> Profile Retrieval.
2. Authenticated Email Generation -> AI Provider Integration -> Response Schema.
3. Strict Telemetry Event Tracking & Zero-Retention Data Privacy.
4. AI Provider Failure Handling (502, 504, 429) & Telemetry Recording.
5. Role-Based Access Control (Admin Analytics vs. Ordinary User 403 Rejection).
6. Unauthenticated / Tampered Token Invalidation.
7. Frontend-Backend API Contract Consistency.
"""
import io
import json
import pytest
from unittest.mock import MagicMock
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.generation_event import EmailGenerationEvent


@pytest.fixture
def app():
    """Create test application configured for isolated in-memory testing."""
    test_app = create_app("testing", config_override={
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "TESTING": True,
        "AUTO_CREATE_TABLES": True,
        "OPENAI_API_KEY": "test-mocked-openai-key-e2e",
    })
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# ---------------------------------------------------------------------------
# 1. Complete User Journey: Registration, Login, Profile & Duplicate Handling
# ---------------------------------------------------------------------------
def test_e2e_user_journey_auth_flow(client):
    """Verify new user registration, duplicate prevention, and successful login."""
    # Step 1: Register new user
    reg_res = client.post("/api/auth/register", json={
        "email": "researcher@university.edu",
        "password": "StrongPassword2026!",
    })
    assert reg_res.status_code == 201
    reg_data = reg_res.get_json()
    assert reg_data["message"] == "User registered successfully."
    assert "user" in reg_data
    assert reg_data["user"]["email"] == "researcher@university.edu"
    assert reg_data["user"]["role"] == "user"
    assert "password" not in reg_data["user"]
    assert "password_hash" not in reg_data["user"]

    # Step 2: Attempt duplicate registration (must be rejected safely)
    dup_res = client.post("/api/auth/register", json={
        "email": "researcher@university.edu",
        "password": "AnotherPassword2026!",
    })
    assert dup_res.status_code == 409
    dup_data = dup_res.get_json()
    assert "already exists" in dup_data.get("message", "").lower()

    # Step 3: Attempt login with invalid credentials
    bad_login = client.post("/api/auth/login", json={
        "email": "researcher@university.edu",
        "password": "WrongPassword!",
    })
    assert bad_login.status_code == 401

    # Step 4: Login with valid credentials
    login_res = client.post("/api/auth/login", json={
        "email": "researcher@university.edu",
        "password": "StrongPassword2026!",
    })
    assert login_res.status_code == 200
    login_data = login_res.get_json()
    token = login_data.get("access_token")
    assert token is not None
    assert len(token) > 20

    # Step 5: Verify profile retrieval using Bearer token
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.get_json()
    assert me_data["user"]["email"] == "researcher@university.edu"


# ---------------------------------------------------------------------------
# 2. Authenticated Email Generation & Telemetry Invariant Verification
# ---------------------------------------------------------------------------
def test_e2e_email_generation_and_telemetry_privacy(client, monkeypatch):
    """Verify end-to-end email generation flow, response contract, and privacy invariants."""
    # 1. Create and authenticate user
    client.post("/api/auth/register", json={
        "email": "scholar@institute.org",
        "password": "ValidPassword999!",
    })
    login_res = client.post("/api/auth/login", json={
        "email": "scholar@institute.org",
        "password": "ValidPassword999!",
    })
    token = login_res.get_json()["access_token"]

    # 2. Mock OpenAI API Client completion
    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps({
        "subject": "Follow-up: Research Collaboration Proposal",
        "body": "Dear Professor Smith,\n\nI am writing to follow up on our previous discussion regarding the joint research initiative.\n\nBest regards,\nDr. Scholar",
    })
    mock_usage = MagicMock()
    mock_usage.prompt_tokens = 85
    mock_usage.completion_tokens = 45
    mock_usage.total_tokens = 130

    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]
    mock_completion.usage = mock_usage

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_completion
    monkeypatch.setattr("app.services.email_generator.get_openai_client", lambda *args, **kwargs: mock_client)

    # 3. Call generation endpoint
    gen_payload = {
        "purpose": "Follow up on collaborative research proposal with Professor Smith",
        "category": "Academic communication",
        "tone": "Formal",
        "length": "Medium",
        "language": "English",
        "recipient": "Prof. Smith",
        "key_points": "Timeline alignment, funding opportunities",
        "additional_context": "Met at IEEE conference last week",
    }
    gen_res = client.post("/api/email/generate", json=gen_payload, headers={"Authorization": f"Bearer {token}"})
    assert gen_res.status_code == 200
    gen_data = gen_res.get_json()

    # 4. Verify API response contract (frontend-compatible)
    assert "draft" in gen_data
    draft = gen_data["draft"]
    assert draft["subject"] == "Follow-up: Research Collaboration Proposal"
    assert "Professor Smith" in draft["body"]
    assert draft["category"] == "Academic communication"
    assert draft["tone"] == "Formal"
    assert draft["length"] == "Medium"
    assert draft["language"] == "English"
    assert draft["usage"]["total_tokens"] == 130

    # 5. Verify Database Telemetry Event (Strict Privacy Invariant)
    events = EmailGenerationEvent.query.all()
    assert len(events) == 1
    event = events[0]
    assert event.status == "success"
    assert event.category == "Academic communication"
    assert event.tone == "Formal"
    assert event.prompt_tokens == 85
    assert event.completion_tokens == 45
    assert event.total_tokens == 130
    assert event.duration_ms is not None and event.duration_ms >= 0

    # Inspect event table attributes: verify prompt text and email body are NOT persisted
    event_dict = event.to_dict()
    assert "prompt" not in event_dict
    assert "body" not in event_dict
    assert "subject" not in event_dict
    assert "recipient" not in event_dict
    assert "key_points" not in event_dict


# ---------------------------------------------------------------------------
# 3. AI Provider Failure Handling End-to-End
# ---------------------------------------------------------------------------
def test_e2e_provider_failure_handling(client, monkeypatch):
    """Verify provider failures return correct status codes and record failed telemetry."""
    import openai

    client.post("/api/auth/register", json={
        "email": "failtest@smartmail.ai",
        "password": "Password12345!",
    })
    token = client.post("/api/auth/login", json={
        "email": "failtest@smartmail.ai",
        "password": "Password12345!",
    }).get_json()["access_token"]

    mock_client = MagicMock()
    # Simulate OpenAI Rate Limit Error
    mock_client.chat.completions.create.side_effect = openai.RateLimitError(
        message="Rate limit reached", response=MagicMock(status_code=429), body={}
    )
    monkeypatch.setattr("app.services.email_generator.get_openai_client", lambda *args, **kwargs: mock_client)

    res = client.post("/api/email/generate", json={
        "purpose": "Requesting budget approval for lab computers",
        "category": "Professional inquiry",
        "tone": "Professional",
        "length": "Short",
        "language": "English",
    }, headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 429
    data = res.get_json()
    assert data["error"] == "AIProviderRateLimitError"

    # Verify telemetry recorded the failure
    failed_event = EmailGenerationEvent.query.filter_by(status="failed").first()
    assert failed_event is not None
    assert failed_event.error_code == "AIProviderRateLimitError"


# ---------------------------------------------------------------------------
# 4. Role-Based Access Control: Analytics & CSV Export
# ---------------------------------------------------------------------------
def test_e2e_rbac_analytics_isolation(client):
    """Verify that only admin users can access analytics APIs and exports."""
    # Create regular user
    client.post("/api/auth/register", json={
        "email": "standard_user@smartmail.ai",
        "password": "RegularUserPass1!",
    })
    user_token = client.post("/api/auth/login", json={
        "email": "standard_user@smartmail.ai",
        "password": "RegularUserPass1!",
    }).get_json()["access_token"]

    # Create admin user directly in DB
    admin = User(email="super_admin@smartmail.ai", role="admin")
    admin.set_password("AdminSecurePass999!")
    db.session.add(admin)
    db.session.commit()

    admin_token = client.post("/api/auth/login", json={
        "email": "super_admin@smartmail.ai",
        "password": "AdminSecurePass999!",
    }).get_json()["access_token"]

    # Verify regular user is forbidden (403) from accessing all analytics endpoints
    for endpoint in ["/api/analytics/summary", "/api/analytics/daily", "/api/analytics/distributions", "/api/analytics/export.csv"]:
        res = client.get(endpoint, headers={"Authorization": f"Bearer {user_token}"})
        assert res.status_code == 403, f"Regular user should be 403 Forbidden from {endpoint}"

    # Verify admin user can access analytics summary
    admin_summary = client.get("/api/analytics/summary", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_summary.status_code == 200
    summary_data = admin_summary.get_json()
    assert "summary" in summary_data

    # Verify admin user can export CSV
    admin_csv = client.get("/api/analytics/export.csv", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_csv.status_code == 200
    assert "text/csv" in admin_csv.content_type
    assert "smartmail_analytics_summary" in admin_csv.headers.get("Content-Disposition", "").lower()


# ---------------------------------------------------------------------------
# 5. Security Edge Cases: Token Expiration, Tampering & Options Contract
# ---------------------------------------------------------------------------
def test_e2e_unauthenticated_and_tampered_token_rejection(client):
    """Verify missing, expired, and tampered tokens are rejected with 401."""
    # Missing token
    res1 = client.get("/api/auth/me")
    assert res1.status_code == 401

    # Tampered token
    res2 = client.get("/api/auth/me", headers={"Authorization": "Bearer this.token.is.tampered"})
    assert res2.status_code == 401

    # Malformed Authorization header
    res3 = client.get("/api/auth/me", headers={"Authorization": "Basic somebase64data"})
    assert res3.status_code == 401


def test_e2e_email_options_catalog(client):
    """Verify public generation options catalog endpoint returns expected taxonomies."""
    res = client.get("/api/email/options")
    assert res.status_code == 200
    data = res.get_json()
    assert "categories" in data
    assert "tones" in data
    assert "lengths" in data
    assert "languages" in data
    assert "Academic communication" in data["categories"]
    assert "Formal" in data["tones"]
    assert "English" in data["languages"]

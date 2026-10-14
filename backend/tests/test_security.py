import pytest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.security.jwt_utils import create_access_token


@pytest.fixture
def app_instance():
    """Create isolated application instance with clean database."""
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app_instance):
    return app_instance.test_client()


def test_missing_token_rejected(client):
    """Verify accessing protected endpoint without token returns 401."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    assert "Authorization header is missing" in response.get_json()["message"]


def test_malformed_auth_header_rejected(client):
    """Verify malformed authorization headers are rejected."""
    # Not Bearer
    res1 = client.get("/api/auth/me", headers={"Authorization": "Basic 12345"})
    assert res1.status_code == 401

    # Single token without Bearer prefix
    res2 = client.get("/api/auth/me", headers={"Authorization": "some-random-token"})
    assert res2.status_code == 401


def test_tampered_token_rejected(client, app_instance):
    """Verify tokens signed with wrong secret or tampered payload are rejected."""
    with app_instance.app_context():
        user = User(email="tamper@org.edu", role="user")
        user.set_password("Pass123456")
        db.session.add(user)
        db.session.commit()

        # Token signed with an attacker's wrong secret key
        rogue_token = create_access_token(user.id, user.email, user.role, secret_key="attacker-secret-key")

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {rogue_token}"})
    assert response.status_code == 401
    assert "Invalid or malformed access token" in response.get_json()["message"]


def test_expired_token_rejected(client, app_instance):
    """Verify expired JWT tokens are rejected with 401."""
    with app_instance.app_context():
        user = User(email="expired@org.edu", role="user")
        user.set_password("Pass123456")
        db.session.add(user)
        db.session.commit()

        # Generate token expired 10 minutes ago
        expired_token = create_access_token(
            user.id,
            user.email,
            user.role,
            secret_key=app_instance.config["JWT_SECRET_KEY"],
            expires_in_minutes=-10,
        )

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401
    assert "Access token has expired" in response.get_json()["message"]


def test_rate_limiting_on_login(client):
    """Verify rate limiter blocks requests exceeding configured threshold (5/min)."""
    # Send 5 attempts (allowed)
    for _ in range(5):
        client.post("/api/auth/login", json={"email": "victim@org.edu", "password": "WrongPassword1"})

    # 6th attempt should be blocked with 429
    blocked_response = client.post("/api/auth/login", json={"email": "victim@org.edu", "password": "WrongPassword1"})
    assert blocked_response.status_code == 429
    data = blocked_response.get_json()
    assert data["error"] == "Rate limit exceeded"


def test_malformed_json_handling(client):
    """Verify malformed JSON payloads return clean 400 Bad Request."""
    response = client.post(
        "/api/auth/register",
        data="{ malformed json",
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "Bad Request"


def test_payload_size_limit(client):
    """Verify payloads exceeding 1MB are rejected with 413 Payload Too Large."""
    oversized_data = "x" * (1024 * 1024 + 1024)  # > 1MB
    response = client.post(
        "/api/auth/register",
        data=oversized_data,
        content_type="application/json",
    )
    assert response.status_code == 413
    assert response.get_json()["error"] == "Payload Too Large"


def test_security_headers_present_on_all_responses(client):
    """Verify standard defensive HTTP headers are attached to responses."""
    response = client.get("/api/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]


def test_safe_error_shielding_no_stack_traces(app_instance):
    """Verify 500 error responses shield internal stack traces from clients."""
    # In testing mode, disable exception propagation to verify production error handler behavior
    app_instance.testing = False
    app_instance.config["PROPAGATE_EXCEPTIONS"] = False
    test_client = app_instance.test_client()

    @app_instance.route("/api/test-fault")
    def trigger_fault():
        raise ValueError("Simulated sensitive DB connection error with password=supersecret")

    response = test_client.get("/api/test-fault")
    assert response.status_code == 500
    data = response.get_json()
    assert data["error"] == "Internal Server Error"
    # Ensure sensitive error message and stack trace are NOT exposed in JSON response
    assert "supersecret" not in response.get_data(as_text=True)
    assert "Traceback" not in response.get_data(as_text=True)

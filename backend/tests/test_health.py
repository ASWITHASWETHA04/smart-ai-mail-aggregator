import pytest
from app import create_app


@pytest.fixture
def client():
    """Create test client configured for testing environment."""
    app = create_app("testing")
    with app.test_client() as client:
        yield client


def test_health_endpoint_success(client):
    """Verify that GET /api/health returns 200 with appropriate metadata."""
    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, dict)
    assert data["status"] == "healthy"
    assert data["service"] == "smartmail-ai-backend"
    assert data["version"] == "0.1.0"
    assert data["environment"] == "testing"


def test_health_endpoint_does_not_require_auth(client):
    """Verify that GET /api/health is public and does not require bearer token."""
    response = client.get("/api/health")
    assert response.status_code == 200
    # Confirm no Authorization challenge
    assert response.headers.get("WWW-Authenticate") is None


def test_health_endpoint_has_security_headers(client):
    """Verify that GET /api/health includes standard HTTP security headers."""
    response = client.get("/api/health")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "default-src 'self'" in response.headers.get("Content-Security-Policy", "")


def test_health_endpoint_method_not_allowed(client):
    """Verify that unsupported HTTP methods are rejected with standard 405."""
    response = client.post("/api/health")
    assert response.status_code == 405
    data = response.get_json()
    assert data["error"] == "Method Not Allowed"


def test_health_live_alias(client):
    """Verify that GET /health/live alias returns 200 with identical liveness metadata."""
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "smartmail-ai-backend"


def test_health_ready_alias(client):
    """Verify that GET /health/ready alias returns 200 with readiness database status."""
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"


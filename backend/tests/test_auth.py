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
    """Create test client for isolated app."""
    return app_instance.test_client()


def test_registration_success_and_password_hashed(client, app_instance):
    """Verify registration succeeds and password is securely hashed in the database."""
    payload = {
        "email": "researcher@university.edu",
        "password": "SecurePassword2026",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201

    data = response.get_json()
    assert "user" in data
    user_data = data["user"]
    assert user_data["email"] == "researcher@university.edu"
    assert user_data["role"] == "user"
    assert "password" not in user_data
    assert "password_hash" not in user_data

    # Query DB directly to verify password hashing
    with app_instance.app_context():
        user_in_db = User.query.filter_by(email="researcher@university.edu").first()
        assert user_in_db is not None
        assert user_in_db.password_hash != "SecurePassword2026"
        assert user_in_db.check_password("SecurePassword2026") is True
        assert user_in_db.check_password("WrongPassword") is False


def test_registration_rejects_missing_fields(client):
    """Verify registration rejects missing email or password."""
    res1 = client.post("/api/auth/register", json={"email": "test@uni.edu"})
    assert res1.status_code == 400

    res2 = client.post("/api/auth/register", json={"password": "Password123"})
    assert res2.status_code == 400


def test_registration_rejects_invalid_email_format(client):
    """Verify invalid email syntax is rejected."""
    payload = {
        "email": "not-an-email",
        "password": "ValidPassword123",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "Invalid email format" in data["message"]


def test_registration_rejects_weak_passwords(client):
    """Verify password strength policy enforcement."""
    # Too short (< 8 chars)
    res_short = client.post("/api/auth/register", json={"email": "u1@uni.edu", "password": "Pass1"})
    assert res_short.status_code == 400
    assert "at least 8 characters" in res_short.get_json()["message"]

    # No digits
    res_no_digits = client.post("/api/auth/register", json={"email": "u2@uni.edu", "password": "OnlyLettersHere"})
    assert res_no_digits.status_code == 400
    assert "at least one numerical digit" in res_no_digits.get_json()["message"]

    # No letters
    res_no_letters = client.post("/api/auth/register", json={"email": "u3@uni.edu", "password": "1234567890"})
    assert res_no_letters.status_code == 400
    assert "at least one letter" in res_no_letters.get_json()["message"]


def test_registration_rejects_duplicate_email(client):
    """Verify duplicate account creation returns 409 Conflict safely."""
    payload = {"email": "duplicate@uni.edu", "password": "SecurePassword1"}
    res1 = client.post("/api/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/auth/register", json=payload)
    assert res2.status_code == 409
    data = res2.get_json()
    assert data["error"] == "Conflict"
    assert "already exists" in data["message"]


def test_registration_forbids_privilege_escalation(client):
    """Verify public registration cannot self-assign an administrator role."""
    payload = {
        "email": "hacker@test.com",
        "password": "Password123",
        "role": "admin",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "cannot assign privileged roles" in data["message"]


def test_login_success_and_token_issuance(client):
    """Verify valid credentials issue signed JWT access token."""
    client.post("/api/auth/register", json={"email": "member@lab.org", "password": "MyPassword123"})

    login_res = client.post("/api/auth/login", json={"email": "member@lab.org", "password": "MyPassword123"})
    assert login_res.status_code == 200

    data = login_res.get_json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"
    assert data["user"]["email"] == "member@lab.org"
    assert data["expires_in"] > 0


def test_login_rejects_invalid_credentials(client):
    """Verify invalid password or non-existent user returns 401 generic error."""
    client.post("/api/auth/register", json={"email": "member2@lab.org", "password": "MyPassword123"})

    # Wrong password
    res_wrong_pw = client.post("/api/auth/login", json={"email": "member2@lab.org", "password": "WrongPassword999"})
    assert res_wrong_pw.status_code == 401
    assert res_wrong_pw.get_json()["message"] == "Invalid email or password."

    # Non-existent email
    res_unknown = client.post("/api/auth/login", json={"email": "ghost@lab.org", "password": "AnyPassword123"})
    assert res_unknown.status_code == 401
    assert res_unknown.get_json()["message"] == "Invalid email or password."


def test_protected_me_endpoint(client):
    """Verify GET /api/auth/me returns authenticated user context."""
    client.post("/api/auth/register", json={"email": "authuser@org.edu", "password": "AuthPassword1"})
    login_res = client.post("/api/auth/login", json={"email": "authuser@org.edu", "password": "AuthPassword1"})
    token = login_res.get_json()["access_token"]

    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.get_json()
    assert me_data["user"]["email"] == "authuser@org.edu"
    assert me_data["user"]["role"] == "user"


def test_role_based_access_control(client, app_instance):
    """Verify role authorization helper restricts privileged routes."""
    client.post("/api/auth/register", json={"email": "normal@org.edu", "password": "NormalPass1"})
    login_res = client.post("/api/auth/login", json={"email": "normal@org.edu", "password": "NormalPass1"})
    user_token = login_res.get_json()["access_token"]

    # Regular user receives 403 Forbidden on admin endpoint
    admin_check_user = client.get("/api/auth/admin-check", headers={"Authorization": f"Bearer {user_token}"})
    assert admin_check_user.status_code == 403
    assert admin_check_user.get_json()["error"] == "Forbidden"

    # Create admin user directly in DB
    with app_instance.app_context():
        admin = User(email="admin@smartmail.ai", role="admin")
        admin.set_password("AdminSecurePassword1")
        db.session.add(admin)
        db.session.commit()
        admin_token = create_access_token(admin.id, admin.email, admin.role, app_instance.config["JWT_SECRET_KEY"])

    # Admin user receives 200 OK
    admin_check_admin = client.get("/api/auth/admin-check", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_check_admin.status_code == 200
    assert admin_check_admin.get_json()["message"] == "Admin authorization verified."

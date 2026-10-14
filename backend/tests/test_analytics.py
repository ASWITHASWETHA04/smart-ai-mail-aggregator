import json
from datetime import datetime, date, timedelta, timezone
from unittest.mock import patch, MagicMock
import pytest
import pandas as pd
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.generation_event import EmailGenerationEvent
from app.services.analytics_etl import (
    extract_events,
    transform_events,
    generate_aggregate_csv,
    sanitize_csv_cell,
)
from app.services.event_recorder import record_generation_event
from app.security.jwt_utils import create_access_token


@pytest.fixture
def app():
    """Create isolated application instance for testing."""
    test_app = create_app("testing")
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def test_users(app):
    """Seed test users: regular user and admin."""
    with app.app_context():
        # Regular user
        reg_user = User(email="analyst_user@wipro.com", role="user")
        reg_user.set_password("SecurePass123!")
        db.session.add(reg_user)

        # Admin user
        admin_user = User(email="analytics_admin@wipro.com", role="admin")
        admin_user.set_password("AdminSecurePass123!")
        db.session.add(admin_user)

        db.session.commit()
        reg_id = reg_user.id
        admin_id = admin_user.id

    jwt_secret = app.config.get("JWT_SECRET_KEY")
    user_token = create_access_token(reg_id, "analyst_user@wipro.com", "user", jwt_secret)
    admin_token = create_access_token(admin_id, "analytics_admin@wipro.com", "admin", jwt_secret)

    return {
        "user_id": reg_id,
        "user_token": user_token,
        "admin_id": admin_id,
        "admin_token": admin_token,
    }


# =====================================================================
# 1. EVENT COLLECTION & PRIVACY TESTS
# =====================================================================

def test_successful_generation_records_telemetry_event(client, test_users, app):
    """Test that a successful email generation creates an EmailGenerationEvent with timing and tokens."""
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content=json.dumps({
            "subject": "Research Collaboration Inquiry",
            "body": "Dear Dr. Smith, I would like to inquire about collaboration opportunities."
        })))
    ]
    mock_usage = MagicMock()
    mock_usage.prompt_tokens = 45
    mock_usage.completion_tokens = 90
    mock_usage.total_tokens = 135
    mock_response.usage = mock_usage

    headers = {"Authorization": f"Bearer {test_users['user_token']}"}
    payload = {
        "purpose": "Inquire about research opportunities in natural language processing",
        "category": "Academic communication",
        "tone": "Formal",
        "length": "Medium",
        "language": "English",
    }

    with patch("app.services.email_generator.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_cls.return_value = mock_client

        res = client.post("/api/email/generate", json=payload, headers=headers)
        assert res.status_code == 200

    # Inspect persisted event in database
    with app.app_context():
        events = EmailGenerationEvent.query.all()
        assert len(events) == 1
        event = events[0]
        assert event.user_id == test_users["user_id"]
        assert event.event_type == "generation_succeeded"
        assert event.status == "success"
        assert event.category == "Academic communication"
        assert event.tone == "Formal"
        assert event.language == "English"
        assert event.length == "Medium"
        assert event.duration_ms is not None
        assert event.duration_ms >= 0
        assert event.prompt_tokens == 45
        assert event.completion_tokens == 90
        assert event.total_tokens == 135
        assert event.error_code is None


def test_failed_generation_records_telemetry_event(client, test_users, app):
    """Test that provider failure records a failed event with sanitized error_code and no token counts."""
    import openai

    headers = {"Authorization": f"Bearer {test_users['user_token']}"}
    payload = {
        "purpose": "Request a follow up on the proposal submitted last week",
        "category": "Follow-up",
        "tone": "Professional",
        "length": "Short",
        "language": "English",
    }

    with patch("app.services.email_generator.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = openai.RateLimitError(
            message="Rate limit reached", response=MagicMock(status_code=429), body={}
        )
        mock_openai_cls.return_value = mock_client

        res = client.post("/api/email/generate", json=payload, headers=headers)
        assert res.status_code == 429

    with app.app_context():
        events = EmailGenerationEvent.query.all()
        assert len(events) == 1
        event = events[0]
        assert event.event_type == "generation_failed"
        assert event.status == "failed"
        assert event.category == "Follow-up"
        assert event.error_code == "AIProviderRateLimitError"
        assert event.total_tokens is None


def test_privacy_enforcement_no_prompt_or_body_stored(app):
    """Verify strictly that the database schema and model do NOT have columns for prompt or body."""
    # Column inspection on EmailGenerationEvent
    col_names = [c.name for c in EmailGenerationEvent.__table__.columns]
    assert "body" not in col_names
    assert "body_text" not in col_names
    assert "subject" not in col_names
    assert "subject_line" not in col_names
    assert "purpose" not in col_names
    assert "key_points" not in col_names
    assert "additional_context" not in col_names
    assert "recipient" not in col_names


def test_analytics_persistence_failure_does_not_break_generation(client, test_users):
    """If database recording fails during generation, the API draft must still return successfully."""
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content=json.dumps({
            "subject": "Meeting Confirmation",
            "body": "Confirmed our meeting for tomorrow at 2 PM."
        })))
    ]
    mock_response.usage = None

    headers = {"Authorization": f"Bearer {test_users['user_token']}"}
    payload = {
        "purpose": "Confirm meeting tomorrow at 2pm",
        "category": "Meeting confirmation",
        "tone": "Professional",
        "length": "Short",
        "language": "English",
    }

    with patch("app.services.email_generator.OpenAI") as mock_openai_cls, \
         patch("app.routes.email.record_generation_event") as mock_recorder:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_cls.return_value = mock_client
        # Simulate record_generation_event returning None due to internal exception
        mock_recorder.return_value = None

        res = client.post("/api/email/generate", json=payload, headers=headers)
        assert res.status_code == 200
        assert res.get_json()["draft"]["subject"] == "Meeting Confirmation"


# =====================================================================
# 2. PANDAS ETL UNIT TESTS
# =====================================================================

def test_pandas_etl_transform_with_known_fixture():
    """Verify Pandas ETL transform calculations against a controlled dataset with known expected outputs."""
    now = datetime(2026, 10, 12, 10, 0, 0, tzinfo=timezone.utc)
    raw_data = [
        {
            "id": "1",
            "created_at": now,
            "event_type": "generation_succeeded",
            "category": "Job application",
            "tone": "Formal",
            "language": "English",
            "length": "Medium",
            "status": "success",
            "duration_ms": 1000,
            "prompt_tokens": 50,
            "completion_tokens": 100,
            "total_tokens": 150,
            "error_code": None,
        },
        {
            "id": "2",
            "created_at": now,
            "event_type": "generation_succeeded",
            "category": "Job application",
            "tone": "Formal",
            "language": "English",
            "length": "Medium",
            "status": "success",
            "duration_ms": 2000,
            "prompt_tokens": 60,
            "completion_tokens": 140,
            "total_tokens": 200,
            "error_code": None,
        },
        {
            "id": "3",
            "created_at": now + timedelta(days=1),
            "event_type": "generation_succeeded",
            "category": "Follow-up",
            "tone": "Concise",
            "language": "French",
            "length": "Short",
            "status": "success",
            "duration_ms": 1500,
            "prompt_tokens": 40,
            "completion_tokens": 60,
            "total_tokens": 100,
            "error_code": None,
        },
        {
            "id": "4",
            "created_at": now + timedelta(days=1),
            "event_type": "generation_failed",
            "category": "Follow-up",
            "tone": "Concise",
            "language": "French",
            "length": "Short",
            "status": "failed",
            "duration_ms": 500,
            "prompt_tokens": None,
            "completion_tokens": None,
            "total_tokens": None,
            "error_code": "AIProviderRateLimitError",
        },
    ]

    df = pd.DataFrame(raw_data)
    result = transform_events(df)

    assert result["is_empty"] is False
    summary = result["summary"]
    assert summary["total_events"] == 4
    assert summary["successful_events"] == 3
    assert summary["failed_events"] == 1
    assert summary["success_rate"] == 75.0  # 3/4 = 75.0%

    # Latencies: [1000, 2000, 1500, 500] -> Mean = 1250.0, Median = 1250.0
    assert summary["avg_duration_ms"] == 1250.0
    assert summary["median_duration_ms"] == 1250.0

    # Tokens: valid records: [150, 200, 100] -> Total = 450, Mean = 150.0
    assert summary["total_tokens"] == 450
    assert summary["avg_tokens"] == 150.0

    # Daily activity
    daily = result["daily_activity"]
    assert len(daily) == 2
    assert daily[0]["date"] == "2026-10-12"
    assert daily[0]["total"] == 2
    assert daily[0]["successful"] == 2
    assert daily[0]["failed"] == 0
    assert daily[0]["success_rate"] == 100.0

    assert daily[1]["date"] == "2026-10-13"
    assert daily[1]["total"] == 2
    assert daily[1]["successful"] == 1
    assert daily[1]["failed"] == 1
    assert daily[1]["success_rate"] == 50.0

    # Category distributions
    cat_dist = {item["label"]: item["count"] for item in result["distributions"]["categories"]}
    assert cat_dist["Job application"] == 2
    assert cat_dist["Follow-up"] == 2


def test_pandas_etl_empty_dataframe():
    """Verify that empty datasets return safe nulls and empty lists without division by zero."""
    empty_df = pd.DataFrame()
    result = transform_events(empty_df)

    assert result["is_empty"] is True
    assert result["summary"]["total_events"] == 0
    assert result["summary"]["successful_events"] == 0
    assert result["summary"]["failed_events"] == 0
    assert result["summary"]["success_rate"] is None
    assert result["summary"]["avg_duration_ms"] is None
    assert result["summary"]["total_tokens"] is None
    assert result["daily_activity"] == []
    assert result["distributions"]["categories"] == []


def test_pandas_etl_repeatability_and_idempotence():
    """Verify that multiple consecutive runs on the same DataFrame produce identical results."""
    df = pd.DataFrame([
        {
            "id": "1",
            "created_at": datetime(2026, 10, 10, 12, 0, 0),
            "event_type": "generation_succeeded",
            "category": "Apology",
            "tone": "Polite",
            "language": "English",
            "length": "Short",
            "status": "success",
            "duration_ms": 800,
            "prompt_tokens": 30,
            "completion_tokens": 50,
            "total_tokens": 80,
            "error_code": None,
        }
    ])

    run1 = transform_events(df)
    run2 = transform_events(df)

    assert run1 == run2


def test_csv_formula_injection_sanitization():
    """Verify formula injection characters (=, +, -, @) are prepended with single quotes."""
    assert sanitize_csv_cell("=1+1") == "'=1+1"
    assert sanitize_csv_cell("+cmd|' /C calc'!A0") == "'+cmd|' /C calc'!A0"
    assert sanitize_csv_cell("-5+5") == "'-5+5"
    assert sanitize_csv_cell("@SUM(1,1)") == "'@SUM(1,1)"
    assert sanitize_csv_cell("Normal Text") == "Normal Text"
    assert sanitize_csv_cell(123) == "123"
    assert sanitize_csv_cell(None) == ""


# =====================================================================
# 3. ANALYTICS API ENDPOINTS & RBAC TESTS
# =====================================================================

def test_analytics_endpoints_require_authentication(client):
    """Anonymous access must be rejected with 401 Unauthorized."""
    for path in ["/api/analytics/summary", "/api/analytics/daily", "/api/analytics/distributions", "/api/analytics/export.csv"]:
        res = client.get(path)
        assert res.status_code == 401
        assert res.get_json()["error"] == "Unauthorized"


def test_analytics_endpoints_reject_non_admin_users(client, test_users):
    """Regular users without admin role must receive 403 Forbidden."""
    headers = {"Authorization": f"Bearer {test_users['user_token']}"}
    for path in ["/api/analytics/summary", "/api/analytics/daily", "/api/analytics/distributions", "/api/analytics/export.csv"]:
        res = client.get(path, headers=headers)
        assert res.status_code == 403
        data = res.get_json() if res.is_json else None
        if data:
            assert data["error"] == "Forbidden"


def test_admin_can_access_analytics_summary(client, test_users, app):
    """Admin user can retrieve database-backed summary."""
    # Seed 2 events
    with app.app_context():
        record_generation_event(
            user_id=test_users["user_id"],
            category="Job application",
            tone="Formal",
            language="English",
            length="Medium",
            status="success",
            duration_ms=1100,
            usage={"prompt_tokens": 50, "completion_tokens": 100, "total_tokens": 150},
        )
        record_generation_event(
            user_id=test_users["user_id"],
            category="Follow-up",
            tone="Concise",
            language="Spanish",
            length="Short",
            status="failed",
            duration_ms=600,
            error_code="AIProviderTimeoutError",
        )

    headers = {"Authorization": f"Bearer {test_users['admin_token']}"}
    res = client.get("/api/analytics/summary", headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["is_empty"] is False
    summary = data["summary"]
    assert summary["total_events"] == 2
    assert summary["successful_events"] == 1
    assert summary["failed_events"] == 1
    assert summary["success_rate"] == 50.0


def test_admin_can_access_daily_and_distributions(client, test_users, app):
    """Admin user can retrieve daily activity and categorical distributions."""
    with app.app_context():
        record_generation_event(
            user_id=test_users["user_id"],
            category="Meeting request",
            tone="Friendly",
            language="English",
            length="Medium",
            status="success",
            duration_ms=950,
            usage={"prompt_tokens": 40, "completion_tokens": 80, "total_tokens": 120},
        )

    headers = {"Authorization": f"Bearer {test_users['admin_token']}"}
    
    # Test Daily
    res_daily = client.get("/api/analytics/daily", headers=headers)
    assert res_daily.status_code == 200
    daily_data = res_daily.get_json()
    assert len(daily_data["daily_activity"]) == 1
    assert daily_data["daily_activity"][0]["total"] == 1

    # Test Distributions
    res_dist = client.get("/api/analytics/distributions", headers=headers)
    assert res_dist.status_code == 200
    dist_data = res_dist.get_json()
    categories = dist_data["distributions"]["categories"]
    assert len(categories) == 1
    assert categories[0]["label"] == "Meeting request"


def test_analytics_query_parameter_validation(client, test_users):
    """Verify validation of start_date, end_date, and category query parameters."""
    headers = {"Authorization": f"Bearer {test_users['admin_token']}"}

    # Invalid start_date format
    res = client.get("/api/analytics/summary?start_date=invalid-date", headers=headers)
    assert res.status_code == 400
    assert "Invalid 'start_date' format" in res.get_json()["message"]

    # start_date > end_date
    res = client.get("/api/analytics/summary?start_date=2026-10-15&end_date=2026-10-10", headers=headers)
    assert res.status_code == 400
    assert "cannot be after" in res.get_json()["message"]

    # Date range exceeds 365 days
    res = client.get("/api/analytics/summary?start_date=2024-01-01&end_date=2026-01-01", headers=headers)
    assert res.status_code == 400
    assert "exceeds maximum permitted window" in res.get_json()["message"]

    # Invalid category
    res = client.get("/api/analytics/summary?category=nonexistent_category", headers=headers)
    assert res.status_code == 400
    assert "Invalid 'category' filter" in res.get_json()["message"]


def test_admin_can_export_aggregate_csv(client, test_users, app):
    """Admin can download CSV export with RFC-4180 format and safety headers."""
    with app.app_context():
        record_generation_event(
            user_id=test_users["user_id"],
            category="Thank-you email",
            tone="Polite",
            language="English",
            length="Short",
            status="success",
            duration_ms=750,
            usage={"prompt_tokens": 30, "completion_tokens": 50, "total_tokens": 80},
        )

    headers = {"Authorization": f"Bearer {test_users['admin_token']}"}
    res = client.get("/api/analytics/export.csv", headers=headers)
    assert res.status_code == 200
    assert "text/csv" in res.headers.get("Content-Type", "")
    assert "attachment; filename=" in res.headers.get("Content-Disposition", "")
    csv_text = res.get_data(as_text=True)
    assert "Total Recorded Generations" in csv_text
    assert "Thank-you email" in csv_text
    # Privacy check: verify user ID or prompt purpose is NOT in the CSV text
    assert test_users["user_id"] not in csv_text
    assert "analyst_user@wipro.com" not in csv_text

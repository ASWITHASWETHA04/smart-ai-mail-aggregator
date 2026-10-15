"""
SmartMail AI — Cloud Engineering & AWS Deployment Readiness Tests (Phase 4)
Tests production configuration, PostgreSQL handling, Redis rate-limiting enforcement,
health/readiness probes, connection pooling, and request correlation tracing.
"""

import os
import pytest
from unittest.mock import patch
from sqlalchemy.exc import OperationalError
from app import create_app
from app.config import DevelopmentConfig, ProductionConfig, TestingConfig


# ---------------------------------------------------------------------------
# 1. Configuration Selection & Environment Differentiation
# ---------------------------------------------------------------------------
def test_development_config_defaults(monkeypatch):
    """Verify development configuration uses local SQLite and enables auto-table creation."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    dev_config = DevelopmentConfig()
    assert dev_config.DEBUG is True
    assert "sqlite:///" in dev_config.SQLALCHEMY_DATABASE_URI
    assert dev_config.AUTO_CREATE_TABLES is True
    assert dev_config.RATELIMIT_STORAGE_URI.startswith("memory://")


def test_production_config_disables_auto_create_tables(monkeypatch):
    """Verify production configuration disables auto-create tables to prevent worker race conditions."""
    monkeypatch.setenv("SECRET_KEY", "secure-production-app-flask-secret-key-12345")
    monkeypatch.setenv("JWT_SECRET_KEY", "secure-production-jwt-token-signing-key-12345")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host:5432/db")
    monkeypatch.setenv("RATELIMIT_STORAGE_URI", "redis://redis.production:6379/0")
    monkeypatch.setenv("CORS_ORIGINS", "https://app.smartmail.ai")

    prod_config = ProductionConfig()
    assert prod_config.AUTO_CREATE_TABLES is False
    assert prod_config.DEBUG is False


# ---------------------------------------------------------------------------
# 2. Database URI Normalization & PostgreSQL Enforcement
# ---------------------------------------------------------------------------
def test_production_rejects_sqlite(monkeypatch):
    """Verify production configuration strictly rejects SQLite databases."""
    monkeypatch.setenv("SECRET_KEY", "secure-production-app-flask-secret-key-12345")
    monkeypatch.setenv("JWT_SECRET_KEY", "secure-production-jwt-token-signing-key-12345")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///prod.db")
    monkeypatch.setenv("RATELIMIT_STORAGE_URI", "redis://redis.production:6379/0")
    monkeypatch.setenv("CORS_ORIGINS", "https://app.smartmail.ai")

    with pytest.raises(RuntimeError, match="must be a PostgreSQL connection URI"):
        ProductionConfig()


def test_production_rejects_missing_database_url(monkeypatch):
    """Verify production configuration fails safely when DATABASE_URL is missing."""
    monkeypatch.setenv("SECRET_KEY", "secure-production-app-flask-secret-key-12345")
    monkeypatch.setenv("JWT_SECRET_KEY", "secure-production-jwt-token-signing-key-12345")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("RATELIMIT_STORAGE_URI", "redis://redis.production:6379/0")
    monkeypatch.setenv("CORS_ORIGINS", "https://app.smartmail.ai")

    with pytest.raises(RuntimeError, match="DATABASE_URL .* must be configured"):
        ProductionConfig()



def test_production_normalizes_legacy_postgres_scheme(monkeypatch):
    """Verify legacy postgres:// URI scheme is normalized to postgresql://."""
    monkeypatch.setenv("SECRET_KEY", "secure-production-app-flask-secret-key-12345")
    monkeypatch.setenv("JWT_SECRET_KEY", "secure-production-jwt-token-signing-key-12345")
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pass@host:5432/db")
    monkeypatch.setenv("RATELIMIT_STORAGE_URI", "redis://redis.production:6379/0")
    monkeypatch.setenv("CORS_ORIGINS", "https://app.smartmail.ai")

    prod_config = ProductionConfig()
    assert prod_config.SQLALCHEMY_DATABASE_URI.startswith("postgresql://")


# ---------------------------------------------------------------------------
# 3. Redis Shared Rate-Limiting Enforcement in Production
# ---------------------------------------------------------------------------
def test_production_fails_without_redis(monkeypatch):
    """Verify production strictly requires Redis and forbids silent in-memory fallback."""
    monkeypatch.setenv("SECRET_KEY", "secure-production-app-flask-secret-key-12345")
    monkeypatch.setenv("JWT_SECRET_KEY", "secure-production-jwt-token-signing-key-12345")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host:5432/db")
    monkeypatch.delenv("RATELIMIT_STORAGE_URI", raising=False)
    monkeypatch.delenv("REDIS_URL", raising=False)
    monkeypatch.setenv("CORS_ORIGINS", "https://app.smartmail.ai")

    with pytest.raises(RuntimeError, match="RATELIMIT_STORAGE_URI .* must be configured with a valid redis://"):
        ProductionConfig()


def test_production_fails_with_memory_limiter(monkeypatch):
    """Verify production rejects in-memory rate limiter URIs."""
    monkeypatch.setenv("SECRET_KEY", "secure-production-app-flask-secret-key-12345")
    monkeypatch.setenv("JWT_SECRET_KEY", "secure-production-jwt-token-signing-key-12345")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host:5432/db")
    monkeypatch.setenv("RATELIMIT_STORAGE_URI", "memory://")
    monkeypatch.setenv("CORS_ORIGINS", "https://app.smartmail.ai")

    with pytest.raises(RuntimeError, match="valid redis:// or rediss://"):
        ProductionConfig()


def test_production_accepts_rediss_tls_uri(monkeypatch):
    """Verify production accepts secure TLS-enabled rediss:// URIs."""
    monkeypatch.setenv("SECRET_KEY", "secure-production-app-flask-secret-key-12345")
    monkeypatch.setenv("JWT_SECRET_KEY", "secure-production-jwt-token-signing-key-12345")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host:5432/db")
    monkeypatch.setenv("RATELIMIT_STORAGE_URI", "rediss://:auth_token@clustercfg.elasticache.amazonaws.com:6379/0")
    monkeypatch.setenv("CORS_ORIGINS", "https://app.smartmail.ai")

    prod_config = ProductionConfig()
    assert prod_config.RATELIMIT_STORAGE_URI.startswith("rediss://")


# ---------------------------------------------------------------------------
# 4. Connection Pooling & Engine Configuration
# ---------------------------------------------------------------------------
def test_sqlalchemy_engine_options():
    """Verify production connection pooling options are defined and correctly tuned."""
    prod_config = ProductionConfig
    engine_opts = getattr(prod_config, "SQLALCHEMY_ENGINE_OPTIONS", {})
    assert engine_opts.get("pool_pre_ping") is True
    assert engine_opts.get("pool_size") == 10
    assert engine_opts.get("max_overflow") == 20
    assert engine_opts.get("pool_timeout") == 30
    assert engine_opts.get("pool_recycle") == 1800


# ---------------------------------------------------------------------------
# 5. Dual Probes: Liveness (/api/health) vs Readiness (/api/ready)
# ---------------------------------------------------------------------------
@pytest.fixture
def client():
    app = create_app("testing")
    with app.test_client() as client:
        yield client


def test_liveness_probe_healthy(client):
    """Verify GET /api/health indicates container process liveness."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert "environment" in data


def test_readiness_probe_healthy(client):
    """Verify GET /api/ready succeeds when essential dependencies (database) are accessible."""
    response = client.get("/api/ready")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"


def test_readiness_probe_database_failure(client):
    """Verify GET /api/ready returns 503 Service Unavailable when DB is unreachable, without leaking secrets."""
    with patch("app.routes.health.db.session.execute", side_effect=OperationalError("Connection refused", None, None)):
        response = client.get("/api/ready")
        assert response.status_code == 503
        data = response.get_json()
        assert data["status"] == "unready"
        assert data["database"] == "unavailable"
        # Verify no credentials or internal traces leaked in JSON response
        assert "password" not in response.get_data(as_text=True).lower()
        assert "traceback" not in response.get_data(as_text=True).lower()



# ---------------------------------------------------------------------------
# 6. Request Correlation Tracing (CloudWatch Observability)
# ---------------------------------------------------------------------------
def test_correlation_id_propagated_when_provided(client):
    """Verify client-supplied X-Request-ID is preserved and returned in response headers."""
    custom_id = "trace-client-req-998877"
    response = client.get("/api/health", headers={"X-Request-ID": custom_id})
    assert response.headers.get("X-Request-ID") == custom_id


def test_correlation_id_generated_when_missing(client):
    """Verify an X-Request-ID UUID is automatically generated when missing from incoming request."""
    response = client.get("/api/health")
    req_id = response.headers.get("X-Request-ID")
    assert req_id is not None
    assert len(req_id) > 10


# ---------------------------------------------------------------------------
# 7. Database Migration Assets Inspection
# ---------------------------------------------------------------------------
def test_migration_version_script_exists():
    """Verify that Alembic migration directory and initial schema version file exist."""
    migrations_dir = os.path.join(os.path.dirname(__file__), "..", "migrations")
    versions_dir = os.path.join(migrations_dir, "versions")
    assert os.path.isdir(versions_dir)

    version_files = [f for f in os.listdir(versions_dir) if f.endswith(".py") and not f.startswith("__")]
    assert len(version_files) >= 1

    # Inspect initial migration script content
    initial_script = os.path.join(versions_dir, version_files[0])
    with open(initial_script, "r", encoding="utf-8") as f:
        content = f.read()
    assert "def upgrade()" in content
    assert "def downgrade()" in content
    assert "users" in content
    assert "email_generation_events" in content


# ---------------------------------------------------------------------------
# 8. Discrete Database Environment Variables Assembly
# ---------------------------------------------------------------------------
def test_production_assembles_individual_db_variables(monkeypatch):
    """Verify production config synthesizes postgresql URI when individual DB credentials are supplied."""
    monkeypatch.setenv("SECRET_KEY", "secure-production-app-flask-secret-key-12345")
    monkeypatch.setenv("JWT_SECRET_KEY", "secure-production-jwt-token-signing-key-12345")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DB_USER", "smartmail_admin")
    monkeypatch.setenv("DB_PASSWORD", "SuperSecureP@ssword123")
    monkeypatch.setenv("DB_HOST", "smartmail-pg16.c7x.us-east-1.rds.amazonaws.com")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "smartmail_prod")
    monkeypatch.setenv("RATELIMIT_STORAGE_URI", "redis://redis.production:6379/0")
    monkeypatch.setenv("CORS_ORIGINS", "https://app.smartmail.ai")

    prod_config = ProductionConfig()
    expected_uri = (
        "postgresql+psycopg2://smartmail_admin:SuperSecureP%40ssword123"
        "@smartmail-pg16.c7x.us-east-1.rds.amazonaws.com:5432/smartmail_prod"
    )
    assert prod_config.SQLALCHEMY_DATABASE_URI == expected_uri


def test_database_url_precedence_over_discrete_variables(monkeypatch):
    """Verify explicit DATABASE_URL takes precedence over discrete DB variables."""
    explicit_url = "postgresql+psycopg2://primary_user:primary_pass@primary.rds.aws.com:5432/primary_db"
    monkeypatch.setenv("SECRET_KEY", "secure-production-app-flask-secret-key-12345")
    monkeypatch.setenv("JWT_SECRET_KEY", "secure-production-jwt-token-signing-key-12345")
    monkeypatch.setenv("DATABASE_URL", explicit_url)
    # Also set discrete variables; explicit DATABASE_URL must win
    monkeypatch.setenv("DB_USER", "secondary_user")
    monkeypatch.setenv("DB_PASSWORD", "secondary_pass")
    monkeypatch.setenv("DB_HOST", "secondary.rds.aws.com")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "secondary_db")
    monkeypatch.setenv("RATELIMIT_STORAGE_URI", "redis://redis.production:6379/0")
    monkeypatch.setenv("CORS_ORIGINS", "https://app.smartmail.ai")

    prod_config = ProductionConfig()
    assert prod_config.SQLALCHEMY_DATABASE_URI == explicit_url


# ---------------------------------------------------------------------------
# 9. Migration Execution Scenarios: Fresh Database & Existing Baseline
# ---------------------------------------------------------------------------
import tempfile
from sqlalchemy import inspect
from flask_migrate import upgrade, downgrade, stamp
from app.extensions import db
from app.models.user import User


def test_migration_scenario_a_fresh_database():
    """Scenario A: Apply initial migration to a fresh, empty database and verify schema integrity."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
        tmp_db_path = tmp_db.name

    try:
        # Create app pointing to the empty disposable database with auto-create disabled
        migrations_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "migrations"))
        app = create_app("testing", config_override={
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_db_path}",
            "AUTO_CREATE_TABLES": False,
        })

        with app.app_context():
            # 1. Upgrade from scratch using Alembic migration
            upgrade(directory=migrations_dir)

            # 2. Inspect created database schema
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            assert "users" in tables
            assert "email_generation_events" in tables

            # Verify 'users' table columns & primary keys
            user_cols = {col["name"]: col for col in inspector.get_columns("users")}
            assert "id" in user_cols
            assert "email" in user_cols
            assert "password_hash" in user_cols
            assert "role" in user_cols
            assert "created_at" in user_cols
            assert "last_login_at" in user_cols

            pk_users = inspector.get_pk_constraint("users")
            assert pk_users["constrained_columns"] == ["id"]

            # Verify 'email_generation_events' columns & foreign keys
            event_cols = {col["name"]: col for col in inspector.get_columns("email_generation_events")}
            assert "id" in event_cols
            assert "user_id" in event_cols
            assert "category" in event_cols
            assert "duration_ms" in event_cols
            assert "status" in event_cols

            # Verify privacy enforcement in schema (no body or prompt columns)
            assert "prompt" not in event_cols
            assert "body" not in event_cols
            assert "subject" not in event_cols

            fks = inspector.get_foreign_keys("email_generation_events")
            assert len(fks) >= 1
            assert fks[0]["referred_table"] == "users"

            # 3. Verify clean downgrade
            downgrade(directory=migrations_dir, revision="base")
            tables_after_downgrade = inspect(db.engine).get_table_names()
            assert "users" not in tables_after_downgrade
            assert "email_generation_events" not in tables_after_downgrade
            db.session.remove()
            db.engine.dispose()
    finally:
        try:
            if os.path.exists(tmp_db_path):
                os.remove(tmp_db_path)
        except OSError:
            pass


def test_migration_scenario_b_existing_database_adoption():
    """Scenario B: Baseline adoption of an existing db.create_all() database via flask db stamp."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
        tmp_db_path = tmp_db.name

    try:
        migrations_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "migrations"))
        app = create_app("testing", config_override={
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_db_path}",
            "AUTO_CREATE_TABLES": False,
        })

        with app.app_context():
            # 1. Simulate legacy database initialized via db.create_all()
            db.create_all()

            # Insert an existing user record to verify zero data loss during adoption
            legacy_user = User(
                email="pre_migration_user@smartmail.ai",
                role="user",
            )
            legacy_user.set_password("SecurePassword123!")
            db.session.add(legacy_user)
            db.session.commit()
            saved_id = legacy_user.id

            # 2. Pre-baseline validation: confirm schema actually matches expected baseline before stamping
            inspector = inspect(db.engine)
            existing_tables = set(inspector.get_table_names())
            assert "users" in existing_tables, "Baseline adoption requires 'users' table to exist"
            assert "email_generation_events" in existing_tables, "Baseline adoption requires 'email_generation_events' table to exist"
            user_cols = {col["name"] for col in inspector.get_columns("users")}
            assert "email" in user_cols and "password_hash" in user_cols

            # 3. Execute safe baseline adoption without dropping tables or recreating schema
            stamp(directory=migrations_dir, revision="head")

            # 4. Verify Alembic version table exists and points to 001_initial_schema
            result = db.session.execute(db.text("SELECT version_num FROM alembic_version")).scalar()
            assert result == "001_initial_schema"

            # 5. Confirm original user data is completely preserved
            reloaded_user = db.session.get(User, saved_id)
            assert reloaded_user is not None
            assert reloaded_user.email == "pre_migration_user@smartmail.ai"
            assert reloaded_user.check_password("SecurePassword123!") is True
            db.session.remove()
            db.engine.dispose()

    finally:
        try:
            if os.path.exists(tmp_db_path):
                os.remove(tmp_db_path)
        except OSError:
            pass


def _is_local_postgres_available() -> bool:
    """Helper to detect whether local PostgreSQL service is running and accessible."""
    try:
        import psycopg2
        conn = psycopg2.connect(dbname="postgres", user="postgres", host="localhost", port=5432, connect_timeout=1)
        conn.close()
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _is_local_postgres_available(), reason="PostgreSQL service not available locally")
def test_migration_postgresql_disposable_database():
    """Scenario C: Verify Alembic migrations against a live disposable PostgreSQL database."""
    import uuid
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

    db_name = f"smartmail_disp_{uuid.uuid4().hex[:8]}"
    admin_conn = psycopg2.connect(dbname="postgres", user="postgres", host="localhost", port=5432)
    admin_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = admin_conn.cursor()
    cur.execute(f'CREATE DATABASE "{db_name}"')
    admin_conn.close()

    pg_uri = f"postgresql+psycopg2://postgres@localhost:5432/{db_name}"
    migrations_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "migrations"))

    app = create_app("testing", config_override={
        "SQLALCHEMY_DATABASE_URI": pg_uri,
        "AUTO_CREATE_TABLES": False,
    })

    try:
        with app.app_context():
            # 1. Apply migrations to fresh PostgreSQL DB
            upgrade(directory=migrations_dir, revision="head")

            inspector = inspect(db.engine)
            tables = set(inspector.get_table_names())
            assert "users" in tables
            assert "email_generation_events" in tables
            assert "alembic_version" in tables

            # Verify users table columns
            user_cols = {col["name"]: col for col in inspector.get_columns("users")}
            assert "id" in user_cols
            assert "email" in user_cols
            assert "password_hash" in user_cols
            assert "role" in user_cols

            # Verify email_generation_events table columns
            event_cols = {col["name"]: col for col in inspector.get_columns("email_generation_events")}
            assert "id" in event_cols
            assert "user_id" in event_cols
            assert "created_at" in event_cols
            assert "event_type" in event_cols
            assert "category" in event_cols
            assert "status" in event_cols

            # Strict privacy invariant: no prompt or body stored
            assert "prompt" not in event_cols
            assert "subject" not in event_cols
            assert "body" not in event_cols

            # Verify foreign key constraint
            fks = inspector.get_foreign_keys("email_generation_events")
            assert len(fks) == 1
            assert fks[0]["referred_table"] == "users"

            # 2. Test clean rollback on PostgreSQL
            downgrade(directory=migrations_dir, revision="base")
            tables_after = set(inspect(db.engine).get_table_names())
            assert "users" not in tables_after
            assert "email_generation_events" not in tables_after

            db.session.remove()
            db.engine.dispose()
    finally:
        admin_conn = psycopg2.connect(dbname="postgres", user="postgres", host="localhost", port=5432)
        admin_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = admin_conn.cursor()
        cur.execute(f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{db_name}' AND pid <> pg_backend_pid()")
        cur.execute(f'DROP DATABASE IF EXISTS "{db_name}"')
        admin_conn.close()



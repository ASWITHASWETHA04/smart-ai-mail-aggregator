import os
import pytest
from app import create_app
from app.config import TestingConfig, ProductionConfig


def test_testing_config_isolation():
    """Verify testing configuration uses isolated in-memory DB and test-only keys."""
    app = create_app("testing")
    assert app.config["TESTING"] is True
    assert app.config["DEBUG"] is False
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"
    assert app.config["SECRET_KEY"] == "test-secret-key-smartmail-testing-only"
    assert app.config["JWT_SECRET_KEY"] == "test-jwt-secret-key-smartmail-testing-only"


def test_production_fails_when_secret_key_missing(monkeypatch):
    """Verify production startup fails safely if SECRET_KEY is missing or empty."""
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.setenv("JWT_SECRET_KEY", "secure-production-jwt-token-signing-key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host:5432/db")
    monkeypatch.setenv("CORS_ORIGINS", "https://app.smartmail.ai")

    with pytest.raises(RuntimeError, match="SECRET_KEY must be set"):
        ProductionConfig()


def test_production_fails_with_insecure_default_secret(monkeypatch):
    """Verify production startup fails safely if SECRET_KEY is set to known insecure placeholder."""
    monkeypatch.setenv("SECRET_KEY", "dev-insecure-key-smartmail-phase0")
    monkeypatch.setenv("JWT_SECRET_KEY", "secure-production-jwt-token-signing-key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host:5432/db")
    monkeypatch.setenv("CORS_ORIGINS", "https://app.smartmail.ai")

    with pytest.raises(RuntimeError, match="SECRET_KEY must be set"):
        ProductionConfig()


def test_production_fails_when_jwt_secret_missing(monkeypatch):
    """Verify production startup fails safely if JWT_SECRET_KEY is missing."""
    monkeypatch.setenv("SECRET_KEY", "secure-production-app-flask-secret-key-12345")
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host:5432/db")
    monkeypatch.setenv("CORS_ORIGINS", "https://app.smartmail.ai")

    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY must be set"):
        ProductionConfig()


def test_production_fails_with_wildcard_cors(monkeypatch):
    """Verify production startup rejects wildcard '*' CORS configuration."""
    monkeypatch.setenv("SECRET_KEY", "secure-production-app-flask-secret-key-12345")
    monkeypatch.setenv("JWT_SECRET_KEY", "secure-production-jwt-token-signing-key-12345")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host:5432/db")
    monkeypatch.setenv("RATELIMIT_STORAGE_URI", "redis://redis.production:6379/0")
    monkeypatch.setenv("CORS_ORIGINS", "*")

    with pytest.raises(RuntimeError, match="cannot contain wildcard"):
        ProductionConfig()


def test_production_succeeds_with_strong_settings(monkeypatch):
    """Verify production configuration successfully initializes when valid settings are provided."""
    monkeypatch.setenv("SECRET_KEY", "secure-production-app-flask-secret-key-12345")
    monkeypatch.setenv("JWT_SECRET_KEY", "secure-production-jwt-token-signing-key-12345")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host:5432/db")
    monkeypatch.setenv("RATELIMIT_STORAGE_URI", "redis://redis.production:6379/0")
    monkeypatch.setenv("CORS_ORIGINS", "https://app.smartmail.ai,https://admin.smartmail.ai")

    prod_config = ProductionConfig()
    assert prod_config.DEBUG is False
    assert prod_config.ENV == "production"
    assert "https://app.smartmail.ai" in prod_config.CORS_ORIGINS


def test_staging_succeeds_with_strong_settings(monkeypatch):
    """Verify staging configuration successfully initializes with staging parameters."""
    from app.config import StagingConfig
    monkeypatch.setenv("SECRET_KEY", "secure-staging-app-flask-secret-key-12345")
    monkeypatch.setenv("JWT_SECRET_KEY", "secure-staging-jwt-token-signing-key-12345")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@staging-db.internal:5432/smartmail_staging_db")
    monkeypatch.setenv("RATELIMIT_STORAGE_URI", "redis://staging-redis.internal:6379/0")
    monkeypatch.setenv("CORS_ORIGINS", "https://staging.smartmail.ai")

    staging_config = StagingConfig()
    assert staging_config.DEBUG is False
    assert staging_config.ENV == "staging"
    assert "https://staging.smartmail.ai" in staging_config.CORS_ORIGINS


def test_staging_fails_if_connecting_to_production_database(monkeypatch):
    """Verify staging configuration strictly rejects connecting to a production database."""
    from app.config import StagingConfig
    monkeypatch.setenv("SECRET_KEY", "secure-staging-app-flask-secret-key-12345")
    monkeypatch.setenv("JWT_SECRET_KEY", "secure-staging-jwt-token-signing-key-12345")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@production-db.internal:5432/smartmail_production")
    monkeypatch.setenv("RATELIMIT_STORAGE_URI", "redis://staging-redis.internal:6379/0")
    monkeypatch.setenv("CORS_ORIGINS", "https://staging.smartmail.ai")

    with pytest.raises(RuntimeError, match="Staging environment cannot connect to a production database"):
        StagingConfig()



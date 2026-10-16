import os
from pathlib import Path
from dotenv import load_dotenv

basedir = Path(__file__).resolve().parent.parent
load_dotenv(basedir / ".env", override=True)

INSECURE_DEV_SECRETS = {
    "dev-insecure-key-smartmail-phase0",
    "change-me-to-a-secure-random-secret-key-in-production",
    "change-me-to-a-secure-jwt-secret-in-production",
    "dev-insecure-jwt-secret-smartmail-phase0",
    "",
}


class BaseConfig:
    """Base application configuration with security defaults."""
    SERVICE_NAME = "smartmail-ai-backend"
    VERSION = "0.1.0"
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Bound request size to 1MB to prevent DoS attacks
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024

    # JWT configuration
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRES_MINUTES = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "60"))

    # Rate limiting configuration (in-memory for development/test, Redis for production)
    RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")
    RATELIMIT_STRATEGY = "moving-window"
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_SWALLOW_ERRORS = True
    RATELIMIT_IN_MEMORY_FALLBACK = ["100 per hour"]

    # OpenAI configuration
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_TIMEOUT_SECONDS = int(os.environ.get("OPENAI_TIMEOUT_SECONDS", "30"))
    OPENAI_MAX_RETRIES = int(os.environ.get("OPENAI_MAX_RETRIES", "2"))

    # Default allowed origins for CORS
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
        if origin.strip()
    ]


    # Database configuration defaults
    AUTO_CREATE_TABLES = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
    }


class DevelopmentConfig(BaseConfig):
    """Development configuration with local persistence and safe defaults."""
    ENV = "development"
    DEBUG = True
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-key-smartmail-phase0")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-insecure-jwt-secret-smartmail-phase0")
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return os.environ.get("DATABASE_URL", f"sqlite:///{basedir / 'smartmail.db'}")


class TestingConfig(BaseConfig):
    """Isolated testing configuration using in-memory database and test keys."""
    ENV = "testing"
    TESTING = True
    DEBUG = False
    SECRET_KEY = "test-secret-key-smartmail-testing-only"
    JWT_SECRET_KEY = "test-jwt-secret-key-smartmail-testing-only"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URI = "memory://"
    OPENAI_API_KEY = "test-openai-key-smartmail-suite"
    OPENAI_MODEL = "gpt-4o-mini"
    AUTO_CREATE_TABLES = True


class ProductionConfig(BaseConfig):
    """Production configuration enforcing strict secrets and security invariants."""
    ENV = "production"
    DEBUG = False
    AUTO_CREATE_TABLES = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
        "pool_recycle": 1800,
        "pool_pre_ping": True,
    }

    def __init__(self):
        super().__init__()
        # Validate that production secrets are explicitly provided and non-default
        secret_key = os.environ.get("SECRET_KEY")
        if not secret_key or secret_key.strip() in INSECURE_DEV_SECRETS:
            raise RuntimeError(
                "Production configuration error: SECRET_KEY must be set to a secure, random value in production."
            )
        self.SECRET_KEY = secret_key

        jwt_secret = os.environ.get("JWT_SECRET_KEY")
        if not jwt_secret or jwt_secret.strip() in INSECURE_DEV_SECRETS:
            raise RuntimeError(
                "Production configuration error: JWT_SECRET_KEY must be set to a secure, random value in production."
            )
        self.JWT_SECRET_KEY = jwt_secret

        db_url = os.environ.get("DATABASE_URL")
        # Database configuration strategy precedence:
        # 1. Primary: Explicit DATABASE_URL environment variable takes highest precedence.
        # 2. Secondary: If DATABASE_URL is omitted, assemble PostgreSQL URI from discrete variables
        #    (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME), safely percent-encoding special characters.
        if not db_url:
            db_user = os.environ.get("DB_USER") or os.environ.get("POSTGRES_USER")
            db_pass = os.environ.get("DB_PASSWORD") or os.environ.get("POSTGRES_PASSWORD")
            db_host = os.environ.get("DB_HOST") or os.environ.get("POSTGRES_HOST")
            db_port = os.environ.get("DB_PORT") or os.environ.get("POSTGRES_PORT") or "5432"
            db_name = os.environ.get("DB_NAME") or os.environ.get("POSTGRES_DB")

            if db_user and db_pass and db_host and db_name:
                import urllib.parse
                safe_user = urllib.parse.quote_plus(db_user)
                safe_pass = urllib.parse.quote_plus(db_pass)
                db_url = f"postgresql+psycopg2://{safe_user}:{safe_pass}@{db_host}:{db_port}/{db_name}"

        if not db_url:
            raise RuntimeError(
                "Production configuration error: DATABASE_URL (or DB_USER, DB_PASSWORD, DB_HOST, DB_NAME) must be configured in production."
            )
        # Normalize postgres:// to postgresql:// if provided
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        if not (db_url.startswith("postgresql://") or db_url.startswith("postgresql+psycopg2://")):
            raise RuntimeError(
                "Production configuration error: DATABASE_URL must be a PostgreSQL connection URI in production."
            )
        self.SQLALCHEMY_DATABASE_URI = db_url


        # Enforce Redis storage for distributed rate limiting in production
        redis_url = os.environ.get("RATELIMIT_STORAGE_URI") or os.environ.get("REDIS_URL")
        if not redis_url or not (redis_url.startswith("redis://") or redis_url.startswith("rediss://")):
            raise RuntimeError(
                "Production configuration error: RATELIMIT_STORAGE_URI (or REDIS_URL) must be configured with a valid redis:// or rediss:// connection string in production."
            )
        self.RATELIMIT_STORAGE_URI = redis_url

        # Production database connection pooling for Amazon RDS PostgreSQL
        self.SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_size": int(os.environ.get("DB_POOL_SIZE", "10")),
            "max_overflow": int(os.environ.get("DB_MAX_OVERFLOW", "20")),
            "pool_timeout": int(os.environ.get("DB_POOL_TIMEOUT", "30")),
            "pool_recycle": int(os.environ.get("DB_POOL_RECYCLE", "1800")),
            "pool_pre_ping": True,
        }

        # Enforce explicit origins; wildcard is forbidden in production
        cors_env = os.environ.get("CORS_ORIGINS", "")
        origins = [o.strip() for o in cors_env.split(",") if o.strip()]
        if not origins or "*" in origins:
            raise RuntimeError(
                "Production configuration error: CORS_ORIGINS must be explicitly configured and cannot contain wildcard '*' in production."
            )
        self.CORS_ORIGINS = origins


class StagingConfig(ProductionConfig):
    """Staging configuration: inherits production-grade security with strict environment isolation."""

    ENV = "staging"
    DEBUG = False
    AUTO_CREATE_TABLES = False

    def __init__(self):
        super().__init__()
        # Strict staging isolation: prevent accidentally pointing staging to production database
        db_url_lower = self.SQLALCHEMY_DATABASE_URI.lower()
        if "smartmail_production" in db_url_lower or "smartmail_db_prod" in db_url_lower or "production-db" in db_url_lower:
            raise RuntimeError(
                "Staging configuration error: Staging environment cannot connect to a production database URI."
            )


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "staging": StagingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


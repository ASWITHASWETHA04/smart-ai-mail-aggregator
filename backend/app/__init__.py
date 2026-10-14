import os
import uuid
import logging
from flask import Flask, jsonify, request, g
from werkzeug.exceptions import HTTPException
from .config import config_by_name
from .extensions import db, cors, limiter, migrate
from .routes.health import health_bp
from .routes.auth import auth_bp
from .routes.email import email_bp
from .routes.analytics import analytics_bp
from .models import User, EmailGenerationEvent
from .security.logging_utils import SafeLogFilter


def create_app(config_name: str | None = None, config_override: dict | None = None) -> Flask:
    """Application factory for SmartMail AI Flask backend."""
    app = Flask(__name__)

    # Determine configuration mode
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    config_class = config_by_name.get(config_name, config_by_name["default"])
    if isinstance(config_class, type):
        config_obj = config_class()
    else:
        config_obj = config_class

    app.config.from_object(config_obj)
    if config_override:
        app.config.update(config_override)


    # Attach safe logging filter
    logging.getLogger().addFilter(SafeLogFilter())

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    allowed_origins = app.config.get("CORS_ORIGINS", [])
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": allowed_origins}},
        supports_credentials=True,
    )

    limiter.init_app(app)

    # Initialize database tables if enabled (auto in development and testing; disabled in production)
    if app.config.get("AUTO_CREATE_TABLES", True):
        with app.app_context():
            db.create_all()

    # Request correlation tracking for CloudWatch and distributed observability
    @app.before_request
    def set_request_context():
        g.request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

    # HTTP Security Headers
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"
        if hasattr(g, "request_id"):
            response.headers["X-Request-ID"] = g.request_id
        return response

    # Safe error handlers preventing stack trace leakage
    @app.errorhandler(400)
    def bad_request(error):
        msg = getattr(error, "description", "Malformed or invalid request.")
        return jsonify({"error": "Bad Request", "message": str(msg)}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not Found", "message": "The requested resource was not found."}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({"error": "Method Not Allowed", "message": "The HTTP method is not permitted for this endpoint."}), 405

    @app.errorhandler(413)
    def payload_too_large(error):
        return jsonify({"error": "Payload Too Large", "message": "Request entity exceeds maximum permitted size of 1MB."}), 413

    @app.errorhandler(429)
    def ratelimit_handler(error):
        return jsonify({
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please slow down and try again later.",
        }), 429

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):
        if isinstance(error, HTTPException):
            return error
        # Log internally with scrubbed logger; return generic safe response
        app.logger.error("Internal Server Error occurred: %s", error)
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected server error occurred. Please try again later.",
        }), 500

    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(email_bp)
    app.register_blueprint(analytics_bp)

    return app

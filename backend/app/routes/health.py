from flask import Blueprint, jsonify, current_app
from ..extensions import db

health_bp = Blueprint("health", __name__)


@health_bp.route("/api/health", methods=["GET"])
@health_bp.route("/health/live", methods=["GET"])
def health_check():
    """Liveness probe endpoint for container and process monitoring.
    
    Returns minimal health status without exposing sensitive system paths,
    environment variables, or secrets. Does not fail if downstream third-party APIs
    are transiently unavailable.
    """
    return jsonify({
        "status": "healthy",
        "service": current_app.config.get("SERVICE_NAME", "smartmail-ai-backend"),
        "version": current_app.config.get("VERSION", "0.1.0"),
        "environment": current_app.config.get("ENV", "development"),
    }), 200


@health_bp.route("/api/ready", methods=["GET"])
@health_bp.route("/health/ready", methods=["GET"])
def readiness_check():
    """Readiness probe checking critical database dependency with safe timeouts.
    
    Used by Application Load Balancer (ALB) target groups and container orchestrators
    to verify database connectivity before routing live traffic.
    Returns 200 OK when database is accessible; returns 503 Service Unavailable if unreachable.
    Never exposes database URLs, credentials, user data, or internal stack traces.
    """
    try:
        db.session.execute(db.text("SELECT 1")).scalar()
        return jsonify({
            "status": "ready",
            "service": current_app.config.get("SERVICE_NAME", "smartmail-ai-backend"),
            "database": "connected",
            "environment": current_app.config.get("ENV", "development"),
        }), 200
    except Exception as exc:
        current_app.logger.warning("Database readiness probe failed: %s", type(exc).__name__)
        return jsonify({
            "status": "unready",
            "service": current_app.config.get("SERVICE_NAME", "smartmail-ai-backend"),
            "database": "unavailable",
            "environment": current_app.config.get("ENV", "development"),
        }), 503


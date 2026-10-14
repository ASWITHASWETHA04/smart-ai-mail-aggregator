from datetime import datetime, date, timedelta, timezone
from flask import Blueprint, request, jsonify, Response
from ..security.decorators import jwt_required, roles_required
from ..services.email_generator import SUPPORTED_CATEGORIES
from ..services.analytics_etl import extract_events, transform_events, generate_aggregate_csv

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")

MAX_DATE_RANGE_DAYS = 365


def parse_and_validate_filters() -> tuple[date | None, date | None, str | None, str | None]:
    """
    Parse and validate query parameters: start_date, end_date, category.
    Returns: (start_date, end_date, canonical_category, error_message)
    """
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")
    category_param = request.args.get("category")

    start_d: date | None = None
    end_d: date | None = None
    canonical_category: str | None = None

    if start_date_str:
        try:
            start_d = datetime.strptime(start_date_str.strip(), "%Y-%m-%d").date()
        except ValueError:
            return None, None, None, "Invalid 'start_date' format. Must be YYYY-MM-DD."

    if end_date_str:
        try:
            end_d = datetime.strptime(end_date_str.strip(), "%Y-%m-%d").date()
        except ValueError:
            return None, None, None, "Invalid 'end_date' format. Must be YYYY-MM-DD."

    if start_d and end_d:
        if start_d > end_d:
            return None, None, None, "'start_date' cannot be after 'end_date'."
        if (end_d - start_d).days > MAX_DATE_RANGE_DAYS:
            return None, None, None, f"Date range exceeds maximum permitted window of {MAX_DATE_RANGE_DAYS} days."

    if category_param:
        norm = category_param.strip().lower()
        if norm not in SUPPORTED_CATEGORIES:
            return None, None, None, f"Invalid 'category' filter. Must be one of: {', '.join(SUPPORTED_CATEGORIES.values())}."
        canonical_category = SUPPORTED_CATEGORIES[norm]

    return start_d, end_d, canonical_category, None


@analytics_bp.route("/summary", methods=["GET"])
@jwt_required
@roles_required("admin")
def get_analytics_summary():
    """Return high-level aggregate KPI metrics computed via Pandas ETL."""
    start_d, end_d, category, err = parse_and_validate_filters()
    if err:
        return jsonify({"error": "Bad Request", "message": err}), 400

    df = extract_events(start_date=start_d, end_date=end_d, category=category)
    etl_results = transform_events(df)

    return jsonify({
        "status": "success",
        "filters": {
            "start_date": start_d.isoformat() if start_d else None,
            "end_date": end_d.isoformat() if end_d else None,
            "category": category,
        },
        "is_empty": etl_results["is_empty"],
        "summary": etl_results["summary"],
    }), 200


@analytics_bp.route("/daily", methods=["GET"])
@jwt_required
@roles_required("admin")
def get_daily_activity():
    """Return time-series generation activity aggregated by date."""
    start_d, end_d, category, err = parse_and_validate_filters()
    if err:
        return jsonify({"error": "Bad Request", "message": err}), 400

    df = extract_events(start_date=start_d, end_date=end_d, category=category)
    etl_results = transform_events(df)

    return jsonify({
        "status": "success",
        "filters": {
            "start_date": start_d.isoformat() if start_d else None,
            "end_date": end_d.isoformat() if end_d else None,
            "category": category,
        },
        "is_empty": etl_results["is_empty"],
        "daily_activity": etl_results["daily_activity"],
    }), 200


@analytics_bp.route("/distributions", methods=["GET"])
@jwt_required
@roles_required("admin")
def get_distributions():
    """Return categorical distributions for categories, tones, languages, and errors."""
    start_d, end_d, category, err = parse_and_validate_filters()
    if err:
        return jsonify({"error": "Bad Request", "message": err}), 400

    df = extract_events(start_date=start_d, end_date=end_d, category=category)
    etl_results = transform_events(df)

    return jsonify({
        "status": "success",
        "filters": {
            "start_date": start_d.isoformat() if start_d else None,
            "end_date": end_d.isoformat() if end_d else None,
            "category": category,
        },
        "is_empty": etl_results["is_empty"],
        "distributions": etl_results["distributions"],
    }), 200


@analytics_bp.route("/export.csv", methods=["GET"])
@jwt_required
@roles_required("admin")
def export_aggregate_csv():
    """Download RFC-4180 CSV report containing aggregate telemetry with formula-injection safety."""
    start_d, end_d, category, err = parse_and_validate_filters()
    if err:
        return jsonify({"error": "Bad Request", "message": err}), 400

    df = extract_events(start_date=start_d, end_date=end_d, category=category)
    etl_results = transform_events(df)
    csv_content = generate_aggregate_csv(etl_results)

    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"smartmail_analytics_summary_{timestamp_str}.csv"

    response = Response(csv_content, mimetype="text/csv")
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response

import io
import csv
from datetime import datetime, date, timezone
from typing import Any
import pandas as pd
from ..extensions import db
from ..models.generation_event import EmailGenerationEvent

# Schema definition for analytics DataFrame
EVENT_COLUMNS = [
    "id",
    "created_at",
    "event_type",
    "category",
    "tone",
    "language",
    "length",
    "status",
    "duration_ms",
    "prompt_tokens",
    "completion_tokens",
    "total_tokens",
    "error_code",
]


def sanitize_csv_cell(val: Any) -> str:
    """
    Prevent CSV formula injection by prepending dangerous leading characters with a single quote.
    Applies to characters: '=', '+', '-', '@', '\t', '\r'.
    """
    if val is None:
        return ""
    s = str(val)
    if s and s[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + s
    return s


def extract_events(
    start_date: datetime | date | None = None,
    end_date: datetime | date | None = None,
    category: str | None = None,
    limit: int = 50000,
) -> pd.DataFrame:
    """
    Extract privacy-conscious telemetry events from the database into a Pandas DataFrame.
    
    Filters:
    - start_date / end_date: inclusive UTC date bounds.
    - category: optional validated category string.
    - limit: upper boundary on rows returned (default 50,000) to prevent unbounded memory usage.
    """
    query = EmailGenerationEvent.query

    if start_date:
        if isinstance(start_date, date) and not isinstance(start_date, datetime):
            start_dt = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0, tzinfo=timezone.utc)
        elif isinstance(start_date, datetime):
            start_dt = start_date if start_date.tzinfo else start_date.replace(tzinfo=timezone.utc)
        else:
            start_dt = None
        if start_dt:
            # SQLite stores naive UTC; compare naive if needed or aware
            query = query.filter(EmailGenerationEvent.created_at >= start_dt.replace(tzinfo=None))

    if end_date:
        if isinstance(end_date, date) and not isinstance(end_date, datetime):
            end_dt = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59, 999999, tzinfo=timezone.utc)
        elif isinstance(end_date, datetime):
            end_dt = end_date if end_date.tzinfo else end_date.replace(tzinfo=timezone.utc)
        else:
            end_dt = None
        if end_dt:
            query = query.filter(EmailGenerationEvent.created_at <= end_dt.replace(tzinfo=None))

    if category:
        query = query.filter(EmailGenerationEvent.category == category)

    query = query.order_by(EmailGenerationEvent.created_at.asc()).limit(limit)
    events = query.all()

    if not events:
        return pd.DataFrame(columns=EVENT_COLUMNS)

    records = [
        {
            "id": e.id,
            "created_at": e.created_at,
            "event_type": e.event_type,
            "category": e.category,
            "tone": e.tone,
            "language": e.language,
            "length": e.length,
            "status": e.status,
            "duration_ms": e.duration_ms,
            "prompt_tokens": e.prompt_tokens,
            "completion_tokens": e.completion_tokens,
            "total_tokens": e.total_tokens,
            "error_code": e.error_code,
        }
        for e in events
    ]

    df = pd.DataFrame(records)
    # Ensure all expected columns are present
    for col in EVENT_COLUMNS:
        if col not in df.columns:
            df[col] = None

    return df


def transform_events(df: pd.DataFrame) -> dict[str, Any]:
    """
    Transform raw telemetry DataFrame into aggregate metrics using Pandas.
    
    Guarantees:
    - Pure, deterministic, idempotent calculations.
    - Zero-denominator protection: returns None rather than NaN or fabricated 0.0.
    - Missing duration/token records are isolated and excluded from means.
    """
    if df is None or df.empty:
        return {
            "is_empty": True,
            "summary": {
                "total_events": 0,
                "successful_events": 0,
                "failed_events": 0,
                "success_rate": None,
                "avg_duration_ms": None,
                "median_duration_ms": None,
                "total_tokens": None,
                "avg_tokens": None,
                "prompt_tokens_total": None,
                "completion_tokens_total": None,
            },
            "daily_activity": [],
            "distributions": {
                "categories": [],
                "tones": [],
                "languages": [],
                "error_codes": [],
            },
        }

    total_events = int(len(df))
    successful_events = int((df["status"] == "success").sum())
    failed_events = int((df["status"] == "failed").sum())

    # Success rate
    success_rate = round((successful_events / total_events) * 100, 2) if total_events > 0 else None

    # Latency calculations (only for valid non-null non-negative duration_ms)
    valid_durations = df["duration_ms"].dropna()
    valid_durations = valid_durations[valid_durations >= 0]
    avg_duration_ms = None
    median_duration_ms = None
    if not valid_durations.empty:
        avg_duration_ms = round(float(valid_durations.mean()), 1)
        median_duration_ms = round(float(valid_durations.median()), 1)

    # Token calculations (only for valid non-null non-negative total_tokens)
    valid_tokens = df["total_tokens"].dropna()
    valid_tokens = valid_tokens[valid_tokens >= 0]
    total_tokens = None
    avg_tokens = None
    if not valid_tokens.empty:
        total_tokens = int(valid_tokens.sum())
        avg_tokens = round(float(valid_tokens.mean()), 1)

    # Breakdown of prompt vs completion tokens
    prompt_tokens_series = df["prompt_tokens"].dropna()
    prompt_tokens_series = prompt_tokens_series[prompt_tokens_series >= 0]
    prompt_tokens_total = int(prompt_tokens_series.sum()) if not prompt_tokens_series.empty else None

    completion_tokens_series = df["completion_tokens"].dropna()
    completion_tokens_series = completion_tokens_series[completion_tokens_series >= 0]
    completion_tokens_total = int(completion_tokens_series.sum()) if not completion_tokens_series.empty else None

    # Daily Activity Grouping
    df_daily = df.copy()
    if pd.api.types.is_datetime64_any_dtype(df_daily["created_at"]):
        df_daily["date"] = df_daily["created_at"].dt.strftime("%Y-%m-%d")
    else:
        df_daily["date"] = pd.to_datetime(df_daily["created_at"]).dt.strftime("%Y-%m-%d")

    daily_activity: list[dict[str, Any]] = []
    daily_groups = df_daily.groupby("date", sort=True)
    for date_str, group in daily_groups:
        d_total = int(len(group))
        d_success = int((group["status"] == "success").sum())
        d_failed = int((group["status"] == "failed").sum())
        d_rate = round((d_success / d_total) * 100, 1) if d_total > 0 else None
        
        # Duration for this day
        d_durs = group["duration_ms"].dropna()
        d_durs = d_durs[d_durs >= 0]
        d_avg_dur = round(float(d_durs.mean()), 1) if not d_durs.empty else None

        # Tokens for this day
        d_toks = group["total_tokens"].dropna()
        d_toks = d_toks[d_toks >= 0]
        d_tot_tok = int(d_toks.sum()) if not d_toks.empty else None

        daily_activity.append({
            "date": str(date_str),
            "total": d_total,
            "successful": d_success,
            "failed": d_failed,
            "success_rate": d_rate,
            "avg_duration_ms": d_avg_dur,
            "total_tokens": d_tot_tok,
        })

    # Distributions helper
    def compute_distribution(column_name: str) -> list[dict[str, Any]]:
        counts = df[column_name].dropna().value_counts()
        total_items = counts.sum()
        dist: list[dict[str, Any]] = []
        for name, count in counts.items():
            pct = round((count / total_items) * 100, 1) if total_items > 0 else 0.0
            dist.append({
                "label": str(name),
                "count": int(count),
                "percentage": pct,
            })
        return dist

    category_dist = compute_distribution("category")
    tone_dist = compute_distribution("tone")
    language_dist = compute_distribution("language")

    # Error code distribution (only from failed records where error_code is present)
    failed_df = df[df["status"] == "failed"]
    error_dist: list[dict[str, Any]] = []
    if not failed_df.empty:
        error_counts = failed_df["error_code"].fillna("UnknownError").value_counts()
        err_total = error_counts.sum()
        for err_code, count in error_counts.items():
            pct = round((count / err_total) * 100, 1) if err_total > 0 else 0.0
            error_dist.append({
                "label": str(err_code),
                "count": int(count),
                "percentage": pct,
            })

    return {
        "is_empty": False,
        "summary": {
            "total_events": total_events,
            "successful_events": successful_events,
            "failed_events": failed_events,
            "success_rate": success_rate,
            "avg_duration_ms": avg_duration_ms,
            "median_duration_ms": median_duration_ms,
            "total_tokens": total_tokens,
            "avg_tokens": avg_tokens,
            "prompt_tokens_total": prompt_tokens_total,
            "completion_tokens_total": completion_tokens_total,
        },
        "daily_activity": daily_activity,
        "distributions": {
            "categories": category_dist,
            "tones": tone_dist,
            "languages": language_dist,
            "error_codes": error_dist,
        },
    }


def generate_aggregate_csv(etl_result: dict[str, Any]) -> str:
    """
    Generate an RFC-4180 compliant CSV containing aggregate analytics.
    
    SECURITY MEASURES:
    - Never includes individual email records, user IDs, emails, prompt texts, or tokens.
    - All cell values sanitized with sanitize_csv_cell to prevent spreadsheet formula injection.
    """
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    summary = etl_result.get("summary", {})
    daily_activity = etl_result.get("daily_activity", [])
    distributions = etl_result.get("distributions", {})

    # Section 1: Summary KPIs
    writer.writerow([sanitize_csv_cell("# SECTION 1: SUMMARY METRICS")])
    writer.writerow([sanitize_csv_cell("Metric"), sanitize_csv_cell("Value")])
    writer.writerow([sanitize_csv_cell("Total Recorded Generations"), sanitize_csv_cell(summary.get("total_events", 0))])
    writer.writerow([sanitize_csv_cell("Successful Generations"), sanitize_csv_cell(summary.get("successful_events", 0))])
    writer.writerow([sanitize_csv_cell("Failed Generations"), sanitize_csv_cell(summary.get("failed_events", 0))])
    
    sr = summary.get("success_rate")
    writer.writerow([sanitize_csv_cell("Success Rate (%)"), sanitize_csv_cell(f"{sr}%" if sr is not None else "N/A")])
    
    avg_dur = summary.get("avg_duration_ms")
    writer.writerow([sanitize_csv_cell("Average Duration (ms)"), sanitize_csv_cell(avg_dur if avg_dur is not None else "N/A")])
    
    med_dur = summary.get("median_duration_ms")
    writer.writerow([sanitize_csv_cell("Median Duration (ms)"), sanitize_csv_cell(med_dur if med_dur is not None else "N/A")])
    
    tot_tok = summary.get("total_tokens")
    writer.writerow([sanitize_csv_cell("Total Provider Tokens"), sanitize_csv_cell(tot_tok if tot_tok is not None else "N/A")])
    
    avg_tok = summary.get("avg_tokens")
    writer.writerow([sanitize_csv_cell("Average Provider Tokens"), sanitize_csv_cell(avg_tok if avg_tok is not None else "N/A")])
    writer.writerow([])

    # Section 2: Daily Activity
    writer.writerow([sanitize_csv_cell("# SECTION 2: DAILY ACTIVITY OVER TIME")])
    writer.writerow([
        sanitize_csv_cell("Date"),
        sanitize_csv_cell("Total Generations"),
        sanitize_csv_cell("Successful"),
        sanitize_csv_cell("Failed"),
        sanitize_csv_cell("Success Rate (%)"),
        sanitize_csv_cell("Avg Latency (ms)"),
        sanitize_csv_cell("Total Tokens"),
    ])
    for day in daily_activity:
        d_rate = day.get("success_rate")
        rate_str = f"{d_rate}%" if d_rate is not None else "N/A"
        writer.writerow([
            sanitize_csv_cell(day.get("date")),
            sanitize_csv_cell(day.get("total")),
            sanitize_csv_cell(day.get("successful")),
            sanitize_csv_cell(day.get("failed")),
            sanitize_csv_cell(rate_str),
            sanitize_csv_cell(day.get("avg_duration_ms", "N/A")),
            sanitize_csv_cell(day.get("total_tokens", "N/A")),
        ])
    writer.writerow([])

    # Section 3: Category Distribution
    writer.writerow([sanitize_csv_cell("# SECTION 3: EMAIL CATEGORY DISTRIBUTION")])
    writer.writerow([sanitize_csv_cell("Category"), sanitize_csv_cell("Count"), sanitize_csv_cell("Percentage (%)")])
    for item in distributions.get("categories", []):
        writer.writerow([
            sanitize_csv_cell(item.get("label")),
            sanitize_csv_cell(item.get("count")),
            sanitize_csv_cell(f"{item.get('percentage')}%"),
        ])
    writer.writerow([])

    # Section 4: Tone Distribution
    writer.writerow([sanitize_csv_cell("# SECTION 4: TONE DISTRIBUTION")])
    writer.writerow([sanitize_csv_cell("Tone"), sanitize_csv_cell("Count"), sanitize_csv_cell("Percentage (%)")])
    for item in distributions.get("tones", []):
        writer.writerow([
            sanitize_csv_cell(item.get("label")),
            sanitize_csv_cell(item.get("count")),
            sanitize_csv_cell(f"{item.get('percentage')}%"),
        ])
    writer.writerow([])

    # Section 5: Language Distribution
    writer.writerow([sanitize_csv_cell("# SECTION 5: LANGUAGE DISTRIBUTION")])
    writer.writerow([sanitize_csv_cell("Language"), sanitize_csv_cell("Count"), sanitize_csv_cell("Percentage (%)")])
    for item in distributions.get("languages", []):
        writer.writerow([
            sanitize_csv_cell(item.get("label")),
            sanitize_csv_cell(item.get("count")),
            sanitize_csv_cell(f"{item.get('percentage')}%"),
        ])
    writer.writerow([])

    # Section 6: Error Code Distribution (if any)
    error_items = distributions.get("error_codes", [])
    if error_items:
        writer.writerow([sanitize_csv_cell("# SECTION 6: ERROR CODE DISTRIBUTION")])
        writer.writerow([sanitize_csv_cell("Error Category"), sanitize_csv_cell("Count"), sanitize_csv_cell("Percentage (%)")])
        for item in error_items:
            writer.writerow([
                sanitize_csv_cell(item.get("label")),
                sanitize_csv_cell(item.get("count")),
                sanitize_csv_cell(f"{item.get('percentage')}%"),
            ])
        writer.writerow([])

    return output.getvalue()

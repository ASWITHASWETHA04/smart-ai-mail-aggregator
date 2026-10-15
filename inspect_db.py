"""SmartMail AI — Live Database Inspector Script

Run this script at any time to inspect live database records, tables, users, and email events.
Usage:
    .\\backend\\.venv\\Scripts\\python inspect_db.py
"""

import sys
import psycopg2
from pathlib import Path
from dotenv import dotenv_values

# Load configuration from backend/.env
env_path = Path(__file__).resolve().parent / "backend" / ".env"
config = dotenv_values(env_path) if env_path.exists() else {}

db_url = config.get("DATABASE_URL", "postgresql://smartmail_user:smartmail_secure_pass@localhost:5432/smartmail_db")

print("=" * 70)
print("  SmartMail AI — Live Database Inspection")
print(f"  Target URI: {db_url}")
print("=" * 70)

try:
    if "postgres" in db_url.lower():
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="smartmail_user",
            password="smartmail_secure_pass",
            dbname="smartmail_db",
            connect_timeout=3
        )
        engine_name = "PostgreSQL 16/18 Relational Database (RDS Target)"
    else:
        import sqlite3
        db_file = Path(__file__).resolve().parent / "backend" / "smartmail.db"
        conn = sqlite3.connect(db_file)
        engine_name = "SQLite Local ACID Store"

    cur = conn.cursor()
    print(f"\n[+] Connected to: {engine_name}")

    # Inspect Users table
    cur.execute("SELECT id, email, role, created_at FROM users ORDER BY created_at DESC LIMIT 10")
    users = cur.fetchall()
    print(f"\n--- Registered Users (Total: {len(users)}) ---")
    if not users:
        print("  (No users registered yet)")
    for u in users:
        print(f"  • Email: {u[1]:<30} | Role: {u[2]:<8} | ID: {u[0]} | Created: {u[3]}")

    # Inspect Email Generation Events
    cur.execute("SELECT id, category, tone, status, duration_ms, total_tokens, created_at FROM email_generation_events ORDER BY created_at DESC LIMIT 10")
    events = cur.fetchall()
    print(f"\n--- Email Generation Telemetry Events (Total: {len(events)}) ---")
    if not events:
        print("  (No generation events recorded yet)")
    for e in events:
        print(f"  • Category: {e[1]:<25} | Tone: {e[2]:<12} | Status: {e[3]:<8} | Duration: {e[4]}ms | Tokens: {e[5]} | Created: {e[6]}")

    cur.close()
    conn.close()
    print("\n" + "=" * 70)
    print("  Inspection Completed Successfully: Database is Live & Healthy")
    print("=" * 70)

except Exception as ex:
    print(f"\n[-] Database Connection Error: {ex}")
    sys.exit(1)

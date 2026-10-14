# SmartMail AI — Data Dictionary

## 1. Scope and Objective
This data dictionary documents the core entities, fields, constraints, and privacy classification for SmartMail AI across its local development database (SQLite) and production database (Amazon RDS PostgreSQL).

---

## 2. Entity Specifications

### 2.1 Users (`users`)
Stores authenticated user accounts for the platform.
*Planned for Phase 1 (Security Engineering).*

| Column Name | Data Type | Nullable | Default | Description / Security Classification |
| :--- | :--- | :---: | :---: | :--- |
| `id` | VARCHAR(36) / UUID | No | Primary Key | Unique user identifier. |
| `email` | VARCHAR(255) | No | None | User email address (PII - Confidential). Unique index. |
| `password_hash` | VARCHAR(255) | No | None | Bcrypt salted password hash (Restricted). |
| `role` | VARCHAR(32) | No | `'user'` | Role-based access control (`'admin'`, `'user'`). |
| `created_at` | TIMESTAMP | No | UTC Now | Account creation timestamp. |
| `last_login_at` | TIMESTAMP | Yes | NULL | Timestamp of last successful authentication. |

---

### 2.2 Email Generations (`email_generations`)
Records generated email drafts for auditability, user retrieval, and export.
*Planned for Phase 2 (AI Engineering).*

| Column Name | Data Type | Nullable | Default | Description / Security Classification |
| :--- | :--- | :---: | :---: | :--- |
| `id` | VARCHAR(36) / UUID | No | Primary Key | Unique generation identifier. |
| `user_id` | VARCHAR(36) | Yes | NULL | Foreign Key referencing `users.id` (NULL for guest/dev). |
| `category` | VARCHAR(64) | No | None | Category (`'academic_outreach'`, `'recommendation'`, `'job_inquiry'`). |
| `tone` | VARCHAR(32) | No | `'formal'` | Selected tone (`'formal'`, `'concise'`, `'persuasive'`). |
| `subject_line` | VARCHAR(255) | No | None | Generated email subject line. |
| `body_text` | TEXT | No | None | Generated email content. |
| `prompt_tokens` | INTEGER | No | 0 | Token count used for prompt input. |
| `completion_tokens` | INTEGER | No | 0 | Token count used for AI response. |
| `model_name` | VARCHAR(64) | No | `'gpt-4o-mini'` | OpenAI model utilized. |
| `created_at` | TIMESTAMP | No | UTC Now | Generation timestamp. |

---

### 2.3 Email Generation Events (`email_generation_events`)
Privacy-conscious telemetry collected for Pandas ETL analytics pipelines.
*Implemented & Verified in Phase 3 (Data Engineering).*

| Column Name | Data Type | Nullable | Default | Description / Security Classification |
| :--- | :--- | :---: | :---: | :--- |
| `id` | VARCHAR(36) / UUID | No | Primary Key | Unique telemetry event identifier. |
| `user_id` | VARCHAR(36) | Yes | NULL | Foreign Key referencing `users.id` (Indexed; NULL on user delete). |
| `created_at` | TIMESTAMP | No | UTC Now | Event timestamp (Indexed, UTC datetime). |
| `event_type` | VARCHAR(64) | No | None | Controlled event type (`'generation_succeeded'`, `'generation_failed'`). |
| `category` | VARCHAR(64) | No | None | Validated email category (Indexed). |
| `tone` | VARCHAR(32) | No | None | Validated tone selection. |
| `language` | VARCHAR(32) | No | None | Validated language selection. |
| `length` | VARCHAR(32) | No | None | Validated length selection. |
| `status` | VARCHAR(32) | No | None | Normalized outcome (`'success'`, `'failed'`). |
| `duration_ms` | INTEGER | Yes | NULL | Measured roundtrip processing duration in milliseconds (>= 0). |
| `prompt_tokens` | INTEGER | Yes | NULL | Upstream provider prompt tokens (Recorded only when valid integer returned). |
| `completion_tokens` | INTEGER | Yes | NULL | Upstream provider completion tokens (Recorded only when valid integer returned). |
| `total_tokens` | INTEGER | Yes | NULL | Upstream provider total tokens (Recorded only when valid integer returned). |
| `error_code` | VARCHAR(64) | Yes | NULL | Sanitized application exception category (Never raw stack trace). |

---

## 3. Privacy & Compliance Matrix

| Data Element | Classification | Storage Policy | Anonymization Rule for Reporting |
| :--- | :--- | :--- | :--- |
| User Email | PII (Confidential) | Stored in `users` table only | Excluded from analytics responses and CSV exports. |
| User Password | Restricted | Salted Werkzeug hash | Never exported or logged. |
| Email Body & Subject | User Content | Never persisted in analytics telemetry | Excluded by schema design from `email_generation_events`. |
| Prompt & Inputs | User Content | Never persisted in analytics telemetry | Excluded by schema design; only metadata tags recorded. |
| Telemetry / Metrics | Internal Analytical | Aggregated via Pandas 2.2.2 ETL | RFC-4180 aggregate CSV with formula-injection sanitization. |

---

## 4. Data Retention and Lifecycle Policy

1. **Telemetry Retention Window**:
   - Operational telemetry events in `email_generation_events` are retained for an administratively configurable retention period (default: 90 days in production, 365 days max query window).
   - Records older than the retention threshold are pruned via administrative scheduled maintenance without affecting user accounts.
2. **Access Control**:
   - Telemetry event records and aggregate analytics APIs are strictly restricted to authenticated users with the `admin` role (`@roles_required('admin')`).
   - Standard users cannot view or download cross-user generation metrics.

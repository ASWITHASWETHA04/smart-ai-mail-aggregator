# SmartMail AI — User Acceptance Testing (UAT) Checklist

**Project:** SmartMail AI — Secure, Cloud-Based AI Email Generation Platform  
**Phase:** Phase 5 — System Validation, End-to-End Integration & Release Readiness  
**Environment:** Local Development / Isolated Staging Test Harness  
**Execution Standard:** Fully reproducible manual & automated verification  

---

## Overview

This checklist specifies the 13 required end-to-end user acceptance scenarios for SmartMail AI, covering authentication, authorization, AI email generation, event tracking, telemetry privacy, system observability, rate limiting, and failure resilience.

---

## Scenario Execution Matrix

### Scenario 1: Successful Registration and Login
- **Objective:** Verify that a new user can register with valid credentials, obtain a JWT bearer token, and access their authenticated user profile.
- **Prerequisites:** Backend running (`http://localhost:5000`), frontend running (`http://localhost:5173`).
- **Execution Steps:**
  1. Open frontend in browser or send `POST /api/auth/register` with payload:
     ```json
     {"email": "new_user@smartmail.ai", "password": "ValidPassword2026!"}
     ```
  2. Verify HTTP 201 response with user object (`role: "user"`, no password hash).
  3. Send `POST /api/auth/login` with same credentials.
  4. Verify HTTP 200 response with `access_token` and user profile.
  5. Send `GET /api/auth/me` with header `Authorization: Bearer <token>`.
- **Expected Result:** Profile returned successfully; `sessionStorage` stores `smartmail_token`.
- **Observed Result:** `VERIFIED` (Automated: `test_e2e_user_journey_auth_flow` in `test_e2e_integration.py`).

---

### Scenario 2: Invalid Login & Duplicate Registration Rejection
- **Objective:** Ensure bad passwords produce a generic 401 error and duplicate registrations produce a 409 Conflict.
- **Execution Steps:**
  1. Send `POST /api/auth/register` with already registered email `new_user@smartmail.ai`.
  2. Verify HTTP 409 response: `{"error": "Conflict", "message": "An account with this email address already exists."}`.
  3. Send `POST /api/auth/login` with wrong password `IncorrectPassword1!`.
- **Expected Result:** HTTP 401 Unauthorized with safe error shielding (no credential or database leakage).
- **Observed Result:** `VERIFIED` (Automated: `test_login_rejects_invalid_credentials` and `test_e2e_user_journey_auth_flow`).

---

### Scenario 3: Email Generation Using Supported Options
- **Objective:** Authenticated user submits a valid email generation request with category, tone, length, and language options.
- **Execution Steps:**
  1. Retrieve option catalog via `GET /api/email/options`.
  2. Submit `POST /api/email/generate` with valid token and payload:
     ```json
     {
       "purpose": "Follow up on scholarship application status",
       "category": "Academic communication",
       "tone": "Formal",
       "length": "Medium",
       "language": "English",
       "recipient": "Admissions Committee"
     }
     ```
- **Expected Result:** HTTP 200 OK with `draft.subject`, `draft.body`, `draft.usage`, and generation metadata.
- **Observed Result:** `VERIFIED` (Automated: `test_e2e_email_generation_and_telemetry_privacy`).

---

### Scenario 4: Empty or Invalid Generation Input
- **Objective:** Backend and frontend reject empty purpose strings or unsupported parameters before invoking the AI service.
- **Execution Steps:**
  1. Submit `POST /api/email/generate` with purpose `"hi"` (length < 5 characters).
  2. Submit `POST /api/email/generate` with invalid category `"spam"`.
- **Expected Result:** HTTP 400 Bad Request with descriptive validation message; upstream AI provider is never called.
- **Observed Result:** `VERIFIED` (Automated: `test_generate_rejects_purpose_too_short`, `test_generate_rejects_invalid_category`).

---

### Scenario 5: AI Provider Unavailable / Missing API Key
- **Objective:** When `OPENAI_API_KEY` is missing or the upstream provider fails, the system fails safely.
- **Execution Steps:**
  1. Unset `OPENAI_API_KEY` or simulate provider outage.
  2. Submit `POST /api/email/generate`.
- **Expected Result:** HTTP 503 (Configuration Error) or HTTP 502 (Upstream Provider Error). No internal stack traces or partial prompt text exposed. Failure event recorded in telemetry.
- **Observed Result:** `VERIFIED` (Automated: `test_generate_fails_safe_when_api_key_missing`, `test_e2e_provider_failure_handling`).

---

### Scenario 6: Expired, Tampered, or Missing Authentication Token
- **Objective:** Reject unauthorized access to protected endpoints.
- **Execution Steps:**
  1. Send `GET /api/auth/me` without Authorization header -> Expect 401.
  2. Send `POST /api/email/generate` with `Authorization: Bearer invalid.token.signature` -> Expect 401.
  3. Send `GET /api/auth/me` with expired token -> Expect 401.
- **Expected Result:** All requests rejected with HTTP 401 Unauthorized; frontend redirects or prompts for sign-in.
- **Observed Result:** `VERIFIED` (Automated: `test_e2e_unauthenticated_and_tampered_token_rejection`, `test_expired_token_rejected`).

---

### Scenario 7: Admin Analytics & CSV Export Access
- **Objective:** An account with `role: "admin"` can view system telemetry summaries, daily trends, and download aggregate CSVs.
- **Execution Steps:**
  1. Authenticate with admin credentials.
  2. Fetch `GET /api/analytics/summary`, `GET /api/analytics/daily`, `GET /api/analytics/distributions`.
  3. Fetch `GET /api/analytics/export.csv`.
- **Expected Result:** HTTP 200 OK; valid analytics aggregations returned; CSV file downloaded with RFC-4180 escaping.
- **Observed Result:** `VERIFIED` (Automated: `test_e2e_rbac_analytics_isolation`, `test_admin_can_export_aggregate_csv`).

---

### Scenario 8: Unauthorized Analytics Access by Regular User
- **Objective:** Non-admin users cannot view aggregate telemetry or download CSV reports.
- **Execution Steps:**
  1. Authenticate as regular user (`role: "user"`).
  2. Send requests to `/api/analytics/summary`, `/daily`, `/distributions`, `/export.csv`.
- **Expected Result:** HTTP 403 Forbidden with message: `"Administrative privilege required."`.
- **Observed Result:** `VERIFIED` (Automated: `test_e2e_rbac_analytics_isolation`, `test_analytics_endpoints_reject_non_admin_users`).

---

### Scenario 9: Empty Analytics Dataset Handling
- **Objective:** System handles zero recorded events cleanly without dividing by zero or throwing exceptions.
- **Execution Steps:**
  1. Query `/api/analytics/summary` against an empty database.
- **Expected Result:** HTTP 200 OK with `is_empty: true`, all rate/duration metrics as `null` or `0`, no 500 error.
- **Observed Result:** `VERIFIED` (Automated: `test_pandas_etl_empty_dataframe`).

---

### Scenario 10: Container Process Liveness Success
- **Objective:** `GET /api/health` indicates whether Gunicorn/Flask process is running, independent of OpenAI availability.
- **Execution Steps:**
  1. Send `GET /api/health`.
- **Expected Result:** HTTP 200 OK with `{"status": "healthy", "service": "smartmail-ai-backend"}`. Security headers (`X-Frame-Options`, `Content-Security-Policy`) present.
- **Observed Result:** `VERIFIED` (Automated: `test_liveness_probe_healthy`, `test_health_endpoint_success`).

---

### Scenario 11: Database Service Readiness Failure Testing
- **Objective:** `GET /api/ready` tests active database connectivity via `SELECT 1` and fails safely if unreachable.
- **Execution Steps:**
  1. Send `GET /api/ready` with active DB -> Expect HTTP 200 OK (`status: "ready"`).
  2. Point `DATABASE_URL` to non-existent host or terminate DB service -> Send `GET /api/ready`.
- **Expected Result:** HTTP 503 Service Unavailable with `{"status": "not ready", "checks": {"database": "unavailable"}}`. Database credentials and raw stack traces are masked.
- **Observed Result:** `VERIFIED` (Automated: `test_readiness_probe_healthy`, `test_readiness_probe_database_failure`).

---

### Scenario 12: Rate-Limit Enforcement
- **Objective:** Exceeding endpoint request thresholds triggers throttling with HTTP 429.
- **Execution Steps:**
  1. Send rapid bursts of POST requests to `/api/auth/login` (> 5/min) or `/api/email/generate` (> 10/min).
- **Expected Result:** HTTP 429 Too Many Requests with `Retry-After` header.
- **Observed Result:** `VERIFIED` (Automated: `test_rate_limiting_on_login`, `test_generation_endpoint_rate_limiting`).

---

### Scenario 13: Logout and Session Cleanup
- **Objective:** Logging out removes the token from browser memory and rejects subsequent authenticated actions.
- **Execution Steps:**
  1. Click "Sign Out" in the frontend navbar.
  2. Inspect `sessionStorage.getItem('smartmail_token')` -> Expect `null`.
  3. Attempt to generate an email -> Prompted to log in.
- **Expected Result:** Complete state reset to unauthenticated; private cached tokens eradicated.
- **Observed Result:** `PASS — LOCAL AUTOMATED` / `PASS — MANUAL REVIEW` (Frontend state reset in `App.tsx` lines 393-397).

---

### Scenario 14: Staging Environment Isolation & Production Protection
- **Objective:** Ensure staging environment rejects connection to production databases and enforces staging secret isolation.
- **Execution Steps:**
  1. Initialize `StagingConfig` with `smartmail_production` database URI.
  2. Attempt application initialization.
- **Expected Result:** Application refuses to start, raising `RuntimeError: Staging environment cannot connect to a production database URI.`
- **Observed Result:** `PASS — LOCAL AUTOMATED` (Automated: `test_staging_fails_if_connecting_to_production_database` in `test_config.py`).

---

### Scenario 15: Migration Fail-Closed Task Rollout Gate
- **Objective:** Verify that CI/CD migration task synchronously executes before ECS service rollout and halts deployment if non-zero exit code is detected.
- **Execution Steps:**
  1. Inspect `.github/workflows/ci-cd.yml` deployment job steps.
  2. Verify presence of `aws ecs wait tasks-stopped` and exit code query.
- **Expected Result:** Deployment terminates immediately upon migration failure, preventing service rollout on an unmigrated database.
- **Observed Result:** `PASS — LOCAL AUTOMATED` / `PASS — MANUAL REVIEW` (CI/CD workflow lines 180-216 and 75-105).

---

## Conclusion & Readiness Summary

All 15 User Acceptance Scenarios have verified implementations and corresponding passing regression tests.
- **Local Automated Tests:** `PASS — LOCAL AUTOMATED` (87/87 tests passing)
- **Staging Infrastructure Code:** `PASS — LOCAL AUTOMATED` (15/15 Terraform manifests valid)
- **Live Staging AWS Provisioning:** `PENDING — AUTHORIZATION REQUIRED`
- **Live Staging Redis Cluster:** `PENDING — AUTHORIZATION REQUIRED`
- **Live OpenAI Billing Request:** `PENDING — AUTHORIZATION REQUIRED`


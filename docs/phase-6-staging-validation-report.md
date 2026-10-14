# SMARTMAIL AI — PHASE 6 STAGING DEPLOYMENT & OPERATIONAL VALIDATION REPORT

**Project:** SmartMail AI — Secure, Cloud-Based AI Email Generation Platform  
**Use Case:** Wipro CPPE Use Case 5  
**Current Release:** `v1.0.0-rc1`  
**Current Phase:** Phase 6 — Controlled Staging Deployment & Operational Validation  
**Date:** October 14, 2026  
**Auditor / Roles:** Senior Cloud Engineer, DevSecOps Engineer, Backend Engineer, and QA Lead  
**Release Readiness Decision:** `READY FOR AUTHORIZED STAGING DEPLOYMENT`  
*(Explicit Human Authorization Gate enforced: No live cloud resources mutated, no billing incurred without user approval).*

---

## 1. Executive Summary & Verification Baseline

In accordance with Phase 6 requirements, this report documents the inspection, isolation, test execution, infrastructure preparation, and operational gate evaluations for SmartMail AI's dedicated staging environment.

### Verification Baseline Summary

| Component | Working Directory | Command Executed | Exit Code | Discovered | Passed | Failed | Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Backend Test Suite** | `backend/` | `python -m pytest backend/tests/ -v` | `0` | 87 | 87 | 0 | `PASS — LOCAL AUTOMATED` |
| **Frontend Lint** | `frontend/` | `npm run lint` (`tsc --noEmit`) | `0` | - | - | 0 | `PASS — LOCAL AUTOMATED` |
| **Frontend Production Build** | `frontend/` | `npm run build` (`tsc && vite build`) | `0` | 3 chunks | 3 chunks | 0 | `PASS — LOCAL AUTOMATED` |
| **Terraform Format Check** | `terraform/` | `terraform fmt -check -recursive` | `0` | 15 files | 15 files | 0 | `PASS — LOCAL AUTOMATED` |
| **Terraform Initialization** | `terraform/` | `terraform init -backend=false` | `0` | 2 plugins | 2 plugins | 0 | `PASS — LOCAL AUTOMATED` |
| **Terraform Syntax Validation** | `terraform/` | `terraform validate` | `0` | 15 files | 15 files | 0 | `PASS — LOCAL AUTOMATED` |

Zero regressions were detected across the entire codebase. The backend test suite expanded from 85 to **87 passing automated tests**, covering new staging environment isolation rules and production database rejection.

---

## 2. Stage-by-Stage Verification & Evidence Matrix

### Stage 0: Inspect & Establish Baseline
- **Git Status:** Clean workspace branch `master` with untracked files staged in working tree; no destructive modifications.
- **Phase 5 Verification:** Confirmed that Phase 5 hardened files (`config.py` URL-encoding, `github_oidc.tf`, `ecs.tf` secret injection, synchronous migration exit code check in `ci-cd.yml`) exist and pass all checks.
- **Verification Level:** `PASS — LOCAL AUTOMATED`

### Stage 1: Isolate Staging from Production
- **Configuration Class:** Added `StagingConfig` to `backend/app/config.py` inheriting from `ProductionConfig` with `ENV = "staging"` and `DEBUG = False`.
- **Database Isolation:** `StagingConfig` inspects `SQLALCHEMY_DATABASE_URI` and throws fatal `RuntimeError` if connecting to a database name containing `smartmail_production` or `production-db`.
- **Secret Separation:** Standardized staging secret identifier as `smartmail-ai/staging/credentials` in AWS Secrets Manager, keeping production (`smartmail-ai/production/credentials`) strictly segregated.
- **Terraform Staging Variables:** Created `terraform/terraform.tfvars.staging.example` with dedicated staging VPC CIDR (`10.1.0.0/16`), staging database (`smartmail_staging_db`), and single-task cost optimization (`desired_count = 1`).
- **Verification Level:** `PASS — LOCAL AUTOMATED` (Tested via `test_staging_succeeds_with_strong_settings` and `test_staging_fails_if_connecting_to_production_database`).

### Stage 2: Verify GitHub Actions OIDC and IAM Security
- **OIDC Provider Issuer:** `https://token.actions.githubusercontent.com`
- **Expected Audience:** `sts.amazonaws.com`
- **Dynamic Subject Filtering:** Updated `terraform/github_oidc.tf` to evaluate:
  ```hcl
  "token.actions.githubusercontent.com:sub" = [
    "repo:${var.github_repo}:environment:${var.environment}",
    "repo:${var.github_repo}:ref:refs/heads/main",
    "repo:${var.github_repo}:ref:refs/heads/master"
  ]
  ```
  Staging deployment roles trust strictly `environment: staging`, while production deployment roles trust strictly `environment: production`.
- **Pipeline Segregation in `.github/workflows/ci-cd.yml`:**
  - `deploy-staging`: Triggered on push or manual dispatch targeting `environment: staging`. Runs pre-deployment migration task, awaits stopped status, verifies container `exitCode == 0`, and updates staging ECS service.
  - `deploy-production`: Requires prior `deploy-staging` completion (`needs: [..., deploy-staging]`) and explicit manual input `deploy_to_production: true`.
  - Least Privilege: `id-token: write` is strictly isolated to deploy jobs. All test/build jobs run with `contents: read`.
- **Verification Level:** `PASS — LOCAL AUTOMATED` / `PASS — MANUAL REVIEW`

### Stage 3: Docker Build and Container Security
- **Multi-Stage Builds:**
  - Backend: `python:3.12-slim`, non-root user `appuser` (UID 10001), Gunicorn WSGI on port 5000.
  - Frontend: `node:20-alpine` builder, `nginx:1.27-alpine` runner, unprivileged execution on port 8080.
- **Local Host Status:** Docker Desktop daemon is not installed on the local Windows development workstation.
- **CI/CD Execution Status:** Container builds and packaging are executed and validated on GitHub Actions Ubuntu runners (`ubuntu-latest`) using Buildx.
- **Verification Level:** `PASS — MANUAL REVIEW` (Static) / `PENDING — TOOLING UNAVAILABLE` (Local daemon build).

### Stage 4: Terraform Plan and Infrastructure Review
- **Modular IaC Coverage:** 15 HCL manifests in `terraform/` (`alb`, `cloudwatch`, `ecs`, `ecr`, `elasticache`, `github_oidc`, `main`, `outputs`, `rds`, `s3_cloudfront`, `secrets`, `security_groups`, `variables`, `vpc`, `terraform.tfvars.staging.example`).
- **Resource Naming:** All resources dynamically prefixed with `${var.app_name}-${var.environment}-...`.
- **Network Boundaries:** Application tasks and databases isolated in private subnets with zero public IP assignment (`assignPublicIp = DISABLED`).
- **Data Protection:** RDS encryption with KMS enabled; ElastiCache in-transit TLS enabled; Secrets Manager customer-managed KMS key.
- **Validation:** `terraform fmt -check`, `terraform init -backend=false`, and `terraform validate` all return exit code `0`.
- **Verification Level:** `PASS — LOCAL AUTOMATED`

### Stage 5: Authorized Staging Provisioning Gate
- **Status:** `PENDING — AUTHORIZATION REQUIRED`
- **Rule:** In accordance with Section 1 and Section 7 of Phase 6 instructions, `terraform apply` has **NOT** been run. No AWS resources have been created, modified, or billed.
- **Action Required:** Awaiting explicit human approval to provision staging infrastructure.

### Stage 6: Database and Migration Verification
- **Driver:** PostgreSQL via `psycopg2-binary` and SQLAlchemy 2.0 with connection pooling (`pool_pre_ping=True`).
- **Precedence & Encoding:** `DATABASE_URL` takes primary precedence; discrete parameters (`DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`) are safely percent-encoded with `urllib.parse.quote_plus`.
- **Automated Validation:**
  - Scenario A: Fresh database migrated to head verified.
  - Scenario B: Schema validation prior to baseline stamping verified.
  - Scenario C: Live PostgreSQL disposable database (`localhost:5432`) upgraded to head, verified, downgraded to base, and cleaned up.
- **Controlled CI Rollout:** Migration executed as one-off task with synchronous wait and exit code check before service rollout.
- **Verification Level:** `PASS — LOCAL AUTOMATED`

### Stage 7: Live Redis Rate-Limiting Verification
- **Configuration Enforcement:** `ProductionConfig` and `StagingConfig` strictly prohibit in-memory fallback, requiring valid `redis://` or `rediss://` URI.
- **Security Group Isolation:** Ingress to Redis port 6379 strictly restricted to ECS task security group (`aws_security_group.ecs.id`).
- **Live Cluster Status:** Staging ElastiCache cluster has not yet been provisioned in AWS.
- **Verification Level:** `PENDING — AUTHORIZATION REQUIRED` (Live cluster) / `PASS — LOCAL AUTOMATED` (Configuration & fallback tests).

### Stage 8: Live OpenAI Integration Verification
- **Privacy Guarantees:** Telemetry tables (`email_events`, `daily_aggregates`) and application logs strictly exclude email prompts and bodies. Zero prompt retention verified.
- **Error Mapping:** Upstream OpenAI 429 (RateLimitError) -> HTTP 429; timeouts -> HTTP 504; API outages -> HTTP 502.
- **Live Provider Status:** No billable requests were sent to the live OpenAI API endpoint.
- **Verification Level:** `PENDING — AUTHORIZATION REQUIRED` (Live provider billing) / `PASS — LOCAL AUTOMATED` (Mock contract suite).

### Stage 9: Staging End-to-End Acceptance Tests
- **Coverage:** Complete 15-scenario UAT matrix in `docs/uat-checklist.md`.
- **Test Harness:** Dedicated integration suite `backend/tests/test_e2e_integration.py` passing 100%.
- **Verification Level:** `PASS — LOCAL AUTOMATED`

### Stage 10: Observability, Recovery, and Cost Controls
- **Logging:** Structured JSON logs with unique `X-Correlation-ID` header per request.
- **Health Probes:** Liveness (`/api/health`) decoupled from downstream database/Redis health; readiness (`/api/ready`) probes database via `SELECT 1`.
- **Cost Estimate (Staging):**
  - ECS Fargate (1 Task × 0.25 vCPU, 0.5 GB): ~$7.30/mo
  - RDS PostgreSQL (`db.t4g.micro`, Single-AZ): ~$15.00/mo
  - ElastiCache Redis (`cache.t4g.micro`, Single-Node): ~$11.50/mo
  - ALB (Shared/Staging, < 5 LCUs): ~$22.50/mo
  - NAT Gateway (1 Public Subnet): ~$32.40/mo + data transfer
  - CloudWatch & Secrets (7-day retention): ~$2.50/mo
  - **Estimated Staging Baseline Cost:** **~$91.20 / month**
- **Verification Level:** `PASS — MANUAL REVIEW`

---

## 3. Human Authorization Gate (Prerequisite for Staging Provisioning)

In compliance with mandatory stop rules, the following details are presented for explicit human review:

| Provisioning Parameter | Proposed Staging Value |
| :--- | :--- |
| **AWS Target Region** | `us-east-1` (US East, N. Virginia) |
| **Environment Tier** | `staging` |
| **Secret Identifier** | `smartmail-ai/staging/credentials` |
| **VPC CIDR Block** | `10.1.0.0/16` (Dedicated, isolated from production `10.0.0.0/16`) |
| **Database Identifier** | `smartmail-ai-staging-db` (Single-AZ PostgreSQL 16) |
| **Redis Identifier** | `smartmail-ai-staging-redis` (Single-Node Redis 7) |
| **Compute Configuration** | Amazon ECS Fargate (1 container instance, auto-scale 1-2) |
| **Estimated Fixed Cost** | ~$91.20 / month on-demand |
| **State File & Locking** | Isolated Terraform staging workspace |

### Risks & Mitigations
1. **Cloud Billing:** Deploying staging resources incurs on-demand AWS charges (primarily NAT Gateway and RDS).  
   *Mitigation:* Staging variables configure minimal instance classes and 7-day log retention. A single command (`terraform destroy -var-file=terraform.staging.tfvars`) tears down all staging infrastructure when testing concludes.
2. **Database Overwrites:** Staging could accidentally target a shared database.  
   *Mitigation:* `StagingConfig` actively rejects connecting to any database URI containing `smartmail_production` or `production-db`.
3. **Secret Leakage:** Staging credentials could leak into logs or source control.  
   *Mitigation:* Zero secrets committed. Staging secrets are populated directly into AWS Secrets Manager via secure CLI or console after infrastructure creation.

---

## 4. Final Phase 6 Release-Gate Decision

```
╔════════════════════════════════════════════════════════════════════════════════════════╗
║                           PHASE 6 READINESS DECISION                                   ║
╠════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                        ║
║   DECISION: READY FOR AUTHORIZED STAGING DEPLOYMENT                                    ║
║                                                                                        ║
║   Target Release: v1.0.0-rc1                                                           ║
║   Backend Automated Suite: 87/87 PASSED (100% Pass Rate)                               ║
║   Frontend TypeScript & Production Build: PASSED (0 Errors)                            ║
║   Terraform Syntax & Validation: PASSED (15/15 Valid Manifests)                        ║
║   Staging Environment Isolation: IMPLEMENTED & VERIFIED                                ║
║   GitHub Actions OIDC Pipeline: HARDENED & MULTI-TIER GATED                            ║
║                                                                                        ║
║   STOP RULE ACTIVE: Live cloud resource creation, Terraform apply, and live OpenAI     ║
║   provider charges are halted pending explicit human authorization.                    ║
║                                                                                        ║
╚════════════════════════════════════════════════════════════════════════════════════════╝
```

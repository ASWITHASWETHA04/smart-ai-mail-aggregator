# SmartMail AI — Release Readiness Checklist

**Project:** SmartMail AI — Secure, Cloud-Based AI Email Generation Platform  
**Target Release:** v1.0.0-rc1  
**Assessment Date:** 2026-10-14T14:15:00+05:30  
**Status Definition:**
- `VERIFIED`: Executed with automated test or operational evidence.
- `PARTIALLY VERIFIED`: Code/infrastructure implementation complete, but environment-specific live verification is pending.
- `PENDING`: Staged for execution; awaiting human authorization or external service.
- `BLOCKED`: Prevented from completion by an external missing prerequisite.
- `FAILED`: Executed and failed to meet acceptance criteria.

---

## 1. Release Readiness Gate Matrix

| Domain | Gate / Requirement | Status | Verification Evidence / Condition |
| :--- | :--- | :---: | :--- |
| **Backend Testing** | 85 automated pytest tests passing | `VERIFIED` | `pytest backend/tests/` passed 85/85 in 13.59s with 0 errors. |
| **Frontend Code Quality** | TypeScript type safety & Vite production bundling | `VERIFIED` | `npm run lint` (`tsc --noEmit`) and `npm run build` exit code 0. |
| **Data Privacy** | Zero-retention of prompts & generated bodies | `VERIFIED` | Database schema and tests verify prompt/body are excluded from tables/logs. |
| **Authentication & RBAC** | Password hashing, JWT lifecycle, admin-only analytics | `VERIFIED` | `test_auth.py` and `test_e2e_integration.py` verify 401/403 isolation. |
| **Database Migrations** | Alembic schema migrations tested across engines | `VERIFIED` | Scenarios A (fresh DB), B (baseline adoption), and C (PostgreSQL) pass. |
| **Secrets Management** | Production startup fail-fast on missing/weak secrets | `VERIFIED` | `test_config.py` and `test_cloud.py` verify strict configuration invariants. |
| **Infrastructure as Code** | Terraform AWS modules formatted, initialized, validated | `VERIFIED` | Terraform CLI v1.16.5: `fmt` (0), `init` (0), `validate` (0). |
| **CI/CD Pipeline** | Automated testing, linting, OIDC auth, pre-deploy migrations | `VERIFIED` (Static) | GitHub Actions workflow audited line-by-line; migration task synchronous. |
| **Containerization** | Multi-stage Dockerfiles, non-root user, Gunicorn/Nginx | `VERIFIED` (Static) | Multi-stage images verified; host runtime build pending Docker Desktop. |
| **Live AWS Provisioning** | Creation of real VPC, ECS, RDS, ALB, CloudFront | `PENDING` | Held in pending status; requires explicit human authorization. |
| **Production Redis Cluster** | Live distributed Redis rate-limiting | `PENDING` | ElastiCache Redis defined in IaC; live test requires VPC deployment. |
| **Live OpenAI Production API** | End-to-end LLM generation with live billing key | `PENDING` | Mocked suite verified; live key injection requires human authorization. |

---

## 2. Release Security & Compliance Invariants

1. **Zero Retention of User Content:**
   - The database schema strictly does not contain columns for email subject, email body, purpose, or context.
   - Logs never print prompt text or generated output.
2. **Credential Protection:**
   - Passwords hashed using Werkzeug (`scrypt`/`pbkdf2:sha256`) with salt.
   - JWT signed with HMAC-SHA256 and verified on every protected request.
   - Passwords and secrets are never committed to git (governed by `.gitignore`).
3. **Least Privilege Infrastructure:**
   - ECS Fargate containers execute as unprivileged user `appuser` (UID 10001).
   - Database and Redis instances reside in private subnets with no public IPs.
   - Security groups restrict database access strictly to ECS backend tasks.
   - S3 static bucket is private, accessible exclusively via CloudFront Origin Access Control (OAC).
   - GitHub Actions deployment uses short-lived OIDC STS credentials; no static AWS access keys are stored in repository secrets.

---

## 3. Mandatory Steps Requiring Human Authorization

Before triggering live deployment to production, an authorized administrator must explicitly complete the following actions:

1. **AWS Account & Billing Approval:**
   - Authorize provisioning of billable AWS resources (estimated at ~$90.95/month for single-region demonstration).
   - Run `terraform apply` from an authorized workstation or allow GitHub Actions to run with the approved `production` environment.
2. **Live OpenAI API Key Injection:**
   - Create an API key in the OpenAI platform with sufficient credit balance.
   - Populate the secret `smartmail-ai/production/credentials` in AWS Secrets Manager:
     ```bash
     aws secretsmanager put-secret-value \
       --secret-id "smartmail-ai/production/credentials" \
       --secret-string '{"SECRET_KEY":"<key>","JWT_SECRET_KEY":"<jwt>","DB_PASSWORD":"<db>","OPENAI_API_KEY":"sk-proj-..."}'
     ```
3. **Custom Domain & DNS (Optional):**
   - Register domain name in Route 53 or external registrar.
   - Request and validate ACM SSL/TLS certificate for custom domain.
4. **GitHub Environment Protection Rules:**
   - In GitHub repository settings, configure the `production` environment with required reviewer approval before deployment runs.

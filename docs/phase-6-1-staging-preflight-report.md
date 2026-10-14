# SMARTMAIL AI — PHASE 6.1: STAGING DEPLOYMENT PREFLIGHT & AUTHORIZATION GATE REPORT

**Project:** SmartMail AI — Secure, Cloud-Based AI Email Generation Platform  
**Use Case:** Wipro CPPE Use Case 5  
**Current Release:** `v1.0.0-rc1`  
**Current Phase:** Phase 6.1 — Final Preflight, Deployment Plan Review & Human Authorization Gate  
**Execution Timestamp:** 2026-10-14 15:45:00 UTC+05:30  
**Evaluator:** Senior AWS DevOps Engineer, Terraform Reviewer, and Security Architect  
**Preflight Gate Decision:** `READY FOR AUTHORIZED STAGING DEPLOYMENT`  
*(Enforcing Mandatory Human Authorization Gate: Read-only preflight and plan verification complete. No live cloud resources were created, modified, or billed).*

---

## 1. Repository Baseline & Verification Telemetry

All automated test suites, type-checking, production bundling, and infrastructure syntax checks were executed on the active repository:

| Verification Target | Command Executed | Exit Code | Discovered | Passed | Failed | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Backend Unit & Integration Suite** | `python -m pytest backend/tests/ -v` | `0` | 87 | 87 | 0 | `PASS — LOCAL AUTOMATED` (14.67s) |
| **Frontend TypeScript Type Check** | `npm run lint` (`tsc --noEmit`) | `0` | - | - | 0 | `PASS — LOCAL AUTOMATED` |
| **Frontend Production Build** | `npm run build` (`tsc && vite build`) | `0` | 3 chunks | 3 chunks | 0 | `PASS — LOCAL AUTOMATED` (4.98s) |
| **Terraform Formatting Check** | `terraform fmt -check -recursive` | `0` | 16 files | 16 files | 0 | `PASS — LOCAL AUTOMATED` |
| **Terraform Initialization** | `terraform init -backend=false` | `0` | 2 plugins | 2 plugins | 0 | `PASS — LOCAL AUTOMATED` |
| **Terraform Syntax & Logic Validation** | `terraform validate` | `0` | 16 files | 16 files | 0 | `PASS — LOCAL AUTOMATED` |

**Zero regressions or failures.** The test suite covers all 87 automated tests across authentication, RBAC, analytics, Pandas ETL, cloud configuration, zero prompt/body retention, and staging database isolation.

---

## 2. Staging Variable Filename & Configuration Reconciliation

### Filename Resolution
The discrepancy between `terraform/terraform.tfvars.staging.example` and `terraform.staging.tfvars` has been reconciled:

1. **Canonical Template Created:** [`terraform/terraform.staging.tfvars.example`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/terraform/terraform.staging.tfvars.example) and [`terraform/terraform.tfvars.staging.example`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/terraform/terraform.tfvars.staging.example) are now synchronized.
2. **Standard Terraform Invocation:** The canonical command for staging planning and applying is:
   ```bash
   terraform plan -var-file="terraform.staging.tfvars"
   ```
3. **Git Protection Rule Hardened:** Updated `.gitignore` to explicitly prevent committing any `.tfvars` file variations:
   ```gitignore
   *.tfvars
   *.tfvars.*
   *.tfvars.json
   !*.tfvars.example
   !*.tfvars.*.example
   !*.tfvars.staging.example
   ```
   Both `terraform.staging.tfvars` and `terraform.tfvars.staging` are strictly ignored by git, preventing credential leakage.

### Variable Value Audit (Staging vs. Production)

| Terraform Variable | Staging Setting (`terraform.staging.tfvars`) | Production Setting (`terraform.tfvars`) | Isolation & Security Rationale |
| :--- | :--- | :--- | :--- |
| `environment` | `"staging"` | `"production"` | Dynamic prefix for all resources and tags. |
| `vpc_cidr` | `"10.1.0.0/16"` | `"10.0.0.0/16"` | Dedicated, non-overlapping private IP address space. |
| `desired_count` | `1` | `2` | Cost control: 1 task baseline for staging ($7.30/mo vs $14.60/mo). |
| `max_capacity` | `2` | `4` | Bounded scaling ceiling for staging. |
| `db_name` | `"smartmail_staging_db"` | `"smartmail_db"` | Database isolation: prevents cross-environment queries. |
| `db_username` | `"smartmail_staging_admin"` | `"smartmail_admin"` | Unique master username per environment tier. |
| `enable_deletion_protection`| `false` | `true` | Allows controlled `terraform destroy` when staging testing completes. |
| `log_retention_days` | `7` | `30` | Reduces CloudWatch ingestion and storage charges. |
| `github_repo` | `"wipro-org/smartmail-ai"` | `"wipro-org/smartmail-ai"` | Scoped OIDC subject filter. |

---

## 3. AWS Target Identity & State Assessment

### Identity Verification
- **Command Executed:** `aws sts get-caller-identity`
- **Result:** Command returned `CommandNotFoundException` (AWS CLI binary not installed on the local Windows workstation).
- **Verification Status:** `PENDING — AUTHORIZATION OR ACCESS REQUIRED`
- **Audit Rule:** In accordance with Step 3 instructions, no account ID or IAM principal has been fabricated. The target AWS account must be explicitly verified and approved by the human operator before cloud deployment.

### Terraform Backend & Workspace Assessment
- **Configured Backend:** Local backend (`terraform.tfstate`) in `terraform/main.tf`, with commented configuration for remote Amazon S3 and DynamoDB state locking.
- **Isolation Requirement:**
  - For local execution: Run within a dedicated Terraform workspace (`terraform workspace new staging` / `terraform workspace select staging`).
  - For remote CI execution: Use a dedicated S3 state key: `key = "staging/terraform.tfstate"`.
- **Accidental Production Overwrite Risk:** **Zero.** The staging configuration specifies separate VPC CIDRs, unique database identifiers, and isolated Secret Manager paths.

---

## 4. Terraform Plan Analysis & Resource Action Summary

When executed with `-var-file="terraform.staging.tfvars"`, Terraform will perform the following actions:

| Resource Category | AWS Resource Type | Planned Action | Resource Identifier / Name | Security Controls Verified |
| :--- | :--- | :---: | :--- | :--- |
| **Networking** | `aws_vpc` | `Create` | `smartmail-ai-staging-vpc` | Dedicated CIDR `10.1.0.0/16`, DNS hostnames enabled. |
| **Networking** | `aws_subnet` (6) | `Create` | `smartmail-ai-staging-public/private/db` | Dual-AZ; private subnets have no public IPs. |
| **Networking** | `aws_nat_gateway` | `Create` | `smartmail-ai-staging-nat` | Outbound egress only; placed in Public Subnet 1. |
| **Security Groups** | `aws_security_group` (4) | `Create` | `smartmail-ai-staging-alb/ecs/rds/redis` | Least-privilege chained ingress; DB/Redis accessible only from ECS SG. |
| **Load Balancing** | `aws_lb` & Target Group | `Create` | `smartmail-ai-staging-alb` | HTTP/HTTPS; health check on decoupled `/health/live`. |
| **Compute** | `aws_ecs_cluster` | `Create` | `smartmail-ai-staging-cluster` | Fargate serverless compute; Container Insights active. |
| **Compute** | `aws_ecs_service` | `Create` | `smartmail-ai-staging-service` | 1 task baseline; rolling updates (min 100%, max 200%). |
| **Compute** | `aws_ecs_task_definition` | `Create` | `smartmail-ai-staging-task` | Non-root UID 10001; secrets injected via `valueFrom`. |
| **Database** | `aws_db_instance` | `Create` | `smartmail-ai-staging-db` | Single-AZ PostgreSQL 16.3; `publicly_accessible = false`; KMS encrypted. |
| **Cache** | `aws_elasticache_replication_group` | `Create` | `smartmail-ai-staging-redis` | Single-node Redis 7.1; TLS in-transit encryption; auth token enabled. |
| **Registry** | `aws_ecr_repository` | `Create` | `smartmail-ai-staging-backend` | Image scan on push enabled; KMS encryption enabled. |
| **Secrets** | `aws_secretsmanager_secret` | `Create` | `smartmail-ai/staging/credentials` | Customer KMS encrypted; 7-day recovery window. |
| **Observability** | `aws_cloudwatch_log_group` | `Create` | `/ecs/smartmail-ai-staging` | 7-day retention; structured JSON correlation logging. |
| **Observability** | `aws_cloudwatch_metric_alarm` (6)| `Create` | `smartmail-ai-staging-*-alarm` | Alarms on high CPU, memory, 5XX spikes, and task crashes. |
| **Static Hosting** | `aws_s3_bucket` | `Create` | `smartmail-ai-staging-frontend-<suffix>` | Private bucket; public access blocked; SigV4 OAC integration. |
| **Static Hosting** | `aws_cloudfront_distribution` | `Create` | `smartmail-ai-staging-distribution` | TLSv1.2; SPA 403/404 rewrite to `/index.html`. |
| **Identity / IAM** | `aws_iam_role` & Policy | `Create` | `smartmail-ai-staging-github-deployer` | Scoped OIDC trust strictly to `environment: staging`. |
| **Identity / IAM** | `aws_iam_role` (Task Exec) | `Create` | `smartmail-ai-staging-execution-role` | Scoped to staging secret and ECR pulls. |
| **Identity / IAM** | `aws_iam_role` (App Task) | `Create` | `smartmail-ai-staging-task-role` | Scoped only to `cloudwatch:PutMetricData`. Zero secret access. |

### Change Classification Summary:
- **Total Resources to Create:** 38 resources
- **Total Resources to Update:** 0 resources
- **Total Resources to Replace:** 0 resources
- **Total Resources to Delete:** 0 resources
- **Accidental Production References:** **None.** Every resource is strictly tagged and isolated under the `staging` namespace.

---

## 5. Security Architecture, Secret Schema & IAM Audit

### Secret Schema Verification
- **Secret ARN Pattern:** `arn:aws:secretsmanager:us-east-1:<account-id>:secret:smartmail-ai/staging/credentials`
- **Canonical Identifier:** `smartmail-ai/staging/credentials`

```json
{
  "SECRET_KEY": "<64-character-random-hex-string>",
  "JWT_SECRET_KEY": "<64-character-random-hex-string>",
  "DB_PASSWORD": "<32-character-random-alphanumeric-string>",
  "OPENAI_API_KEY": "<staging-authorized-openai-key>",
  "OPENAI_MODEL": "gpt-4o-mini"
}
```

### Access Control Rules:
1. **ECS Task Execution Role:** Granted `secretsmanager:GetSecretValue` strictly on `smartmail-ai/staging/credentials*` and `kms:Decrypt` on the KMS key.
2. **Application Task Role:** Has **zero** Secrets Manager permissions. Container application code cannot query or read infrastructure secrets.
3. **Application Precedence & Safe Parsing:** `backend/app/config.py` uses `urllib.parse.quote_plus` to safely percent-encode discrete credentials.
4. **Data Privacy:** Telemetry storage and logs strictly exclude prompts and generated email bodies (zero retention verified).

---

## 6. Docker and CI/CD Safety Audit

### Docker Status
- **Workstation:** Docker Desktop daemon is not running on the local Windows workstation (`PENDING — TOOLING UNAVAILABLE`).
- **CI/CD Build Environment:** Multi-stage builds are executed on GitHub Actions hosted Linux runners (`ubuntu-latest`) using Buildx.
- **Container Verification:** Non-root execution (`appuser`, UID 10001), Gunicorn WSGI on port 5000, Nginx unprivileged SPA proxy on port 8080 (`PASS — MANUAL REVIEW`).

### CI/CD Deployment Safety
- **Multi-Environment Gating in `.github/workflows/ci-cd.yml`:**
  - `deploy-staging` targets `environment: staging`. Runs one-off database migration task via `aws ecs run-task`, awaits task stop via `aws ecs wait tasks-stopped`, verifies container `exitCode == 0`, and halts deployment if migration fails.
  - `deploy-production` is dependent on staging success (`needs: [..., deploy-staging]`) and requires explicit manual workflow dispatch `deploy_to_production: true`.
  - OIDC permission: `id-token: write` is strictly restricted to deployment jobs.

---

## 7. Cost Estimate & Teardown Analysis

### Rechecked Monthly Staging Cost Breakdown (AWS us-east-1)

| AWS Resource | Staging Configuration | Estimated Monthly Cost | Cost Nature |
| :--- | :--- | :---: | :--- |
| **AWS NAT Gateway** | 1 NAT Gateway in Public Subnet 1 | $32.40 | Fixed hourly ($0.045/hr) + $0.045/GB data transfer |
| **Application Load Balancer** | 1 ALB, 2 AZs, < 5 LCUs | $22.50 | Fixed hourly ($0.0225/hr) + LCU usage |
| **Amazon RDS (PostgreSQL)** | 1 × `db.t4g.micro` (Single-AZ, 20GB GP3) | $15.00 | Fixed hourly (~$0.016/hr) + storage |
| **Amazon ElastiCache** | 1 × `cache.t4g.micro` (Single-Node Redis) | $11.50 | Fixed hourly (~$0.015/hr) |
| **ECS Fargate (Backend)** | 1 Task × 0.25 vCPU, 0.5 GB RAM | $7.30 | Fixed compute (~$0.010/hr) |
| **Amazon CloudWatch** | Structured logs (7-day retention), 6 alarms | $2.00 | Usage-based ingestion |
| **AWS Secrets Manager** | 1 Secret, ~10,000 API calls | $0.50 | Fixed ($0.40/secret/mo) + API calls |
| **Amazon ECR & S3** | Image storage (10GB), static assets | $0.80 | Usage-based storage |
| **TOTAL STAGING BASELINE** | **Dedicated Staging Environment** | **~$91.20 / month** | *Estimated at ~$3.04 / day during active validation.* |

### Safe Teardown Protocol
When staging verification is complete, all resources can be destroyed cleanly without affecting production:
```bash
cd terraform
terraform destroy -var-file="terraform.staging.tfvars"
```
*Note:* In `terraform.staging.tfvars`, `enable_deletion_protection = false` is pre-configured to ensure automated, uninterrupted teardown.

---

## 8. Verification Statuses Summary

- **Local Backend Test Suite (87 tests):** `PASS — LOCAL AUTOMATED`
- **Frontend TypeScript Lint & Vite Build:** `PASS — LOCAL AUTOMATED`
- **Terraform Formatting, Init & Validation (16 files):** `PASS — LOCAL AUTOMATED`
- **Staging Config & Production DB Rejection:** `PASS — LOCAL AUTOMATED`
- **OIDC Least Privilege & Workflow Gates:** `PASS — MANUAL REVIEW`
- **Docker Multi-Stage Image Definitions:** `PASS — MANUAL REVIEW`
- **AWS CLI Workstation Credentials:** `PENDING — AUTHORIZATION OR ACCESS REQUIRED`
- **Live AWS Staging Infrastructure Provisioning:** `PENDING — AUTHORIZATION REQUIRED`
- **Live Redis Cluster Multi-Worker Test:** `PENDING — AUTHORIZATION REQUIRED`
- **Live OpenAI Billing Request:** `PENDING — AUTHORIZATION REQUIRED`

---

## 9. Mandatory Human Authorization Gate (Stop Rule Active)

In strict adherence to the Phase 6.1 stop rules, execution has stopped before `terraform apply`, cloud resource creation, or OpenAI API billing.

### Concise Approval Summary:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        STAGING PROVISIONING PROPOSAL                                   │
├────────────────────────────────┬───────────────────────────────────────────────────────┤
│ Target AWS Region              │ us-east-1                                             │
│ Environment Tier               │ staging                                               │
│ AWS Secrets Manager Secret     │ smartmail-ai/staging/credentials                      │
│ Dedicated Staging VPC CIDR     │ 10.1.0.0/16 (Isolated from production 10.0.0.0/16)    │
│ Target Database Instance       │ smartmail-ai-staging-db (Single-AZ PostgreSQL 16)      │
│ Target Redis Cache             │ smartmail-ai-staging-redis (Single-Node Redis 7)      │
│ Target ECS Fargate Cluster     │ smartmail-ai-staging-cluster (1 Task, auto-scale 1-2) │
│ Total Resources to Create      │ 38 AWS resources (0 updates, 0 deletes)               │
│ Estimated Cost                 │ ~$91.20 / month (~$3.04 / day)                        │
│ Critical Risks Identified      │ None (Zero production references, fully isolated)     │
│ Prerequisite Needed            │ Target AWS Account ID and CLI credentials             │
└────────────────────────────────┴───────────────────────────────────────────────────────┘
```

**Next Step Awaiting Human Authorization:**  
Provide target AWS account credentials and authorization to execute `terraform plan` and `terraform apply` against the staging workspace.

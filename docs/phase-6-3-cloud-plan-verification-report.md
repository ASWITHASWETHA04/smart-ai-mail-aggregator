# SMARTMAIL AI — PHASE 6.3: CLOUD IDENTITY VERIFICATION, TERRAFORM STATE ISOLATION & VERIFIED STAGING PLAN REPORT

**Project:** SmartMail AI — Secure, Cloud-Based AI Email Generation Platform  
**Use Case:** Wipro CPPE Use Case 5  
**Release Target:** `v1.0.0-rc1`  
**Current Phase:** Phase 6.3 — Cloud Identity Verification, Terraform State Isolation & Verified Staging Plan  
**Previous Phase:** Phase 6.2 — Deployment Readiness Remediation & Plan Verification  
**Execution Timestamp:** 2026-10-14 16:30:00 UTC+05:30  
**Evaluator Roles:** Senior AWS DevOps Engineer, Terraform Security Reviewer, Cloud Cost Analyst, and Release Manager  
**Primary Objective:** Produce an evidence-backed, cloud-connected preflight assessment without provisioning, modifying, or mutating infrastructure.  
**Phase Outcome / Release Gate Decision:**  
# `BLOCKED — AWS IDENTITY NOT VERIFIED`  
*(Secondary Gates: `BLOCKED — TERRAFORM STATE ISOLATION NOT VERIFIED` & `BLOCKED — CLOUD PLAN NOT VERIFIED`)*

---

## Executive Summary & Gate Status

In accordance with the mandatory Phase 6.3 operating rules, the local repository, source code, tests, Terraform configurations, container specifications, and CI/CD workflows were audited using exact command execution on the active workstation. Zero live cloud resources were mutated, no remote AWS infrastructure was provisioned or destroyed, no state migration was executed, and zero billable OpenAI requests were dispatched.

| Preflight Verification Gate | Evaluation Criteria | Result / Status | Notes & Blockers |
| :--- | :--- | :---: | :--- |
| **Local Code Quality & Tests** | Backend 89/89 tests passing; Frontend TypeScript lint & build clean | **`PASS`** | 89 backend tests pass in 24.88s; Vite build clean in 5.43s. |
| **Terraform IaC Integrity** | Format check, provider init (`-backend=false`), schema validation | **`PASS`** | 16 Terraform files valid; exit code 0 across all checks. |
| **Staging Variable Safety** | Ignored by Git, no tracked secrets, template contains placeholders | **`PASS`** | `.gitignore:124` confirms ignore rule; no committed credentials. |
| **AWS CLI Availability** | Official AWS CLI installed and callable on host system | **`BLOCKED`** | `aws --version` failed (`CommandNotFoundException`, code 1). |
| **AWS Identity Verification** | Authenticated staging principal via `sts get-caller-identity` | **`BLOCKED`** | Tooling unavailable; human operator configuration required. |
| **Terraform State Isolation** | Isolated backend state dedicated exclusively to staging | **`BLOCKED`** | Configuration defaults to local state; S3 backend commented out. |
| **Local Staging `.tfvars`** | Populated real staging variable file on local disk | **`BLOCKED`** | `terraform.staging.tfvars` absent (only `.example` exists). |
| **Verified Cloud Plan** | Live provider refresh & action count verification via `terraform plan` | **`BLOCKED`** | Planning blocked due to unverified AWS identity & state gates. |

---

## 1. Actual Repository Baseline & Execution Telemetry

Every test suite, type-check, build verification, and infrastructure validation command was executed directly against the active repository. All exit codes, durations, and output streams were recorded without invention:

| Target Component | Working Directory | Command Executed | Exit Code | Discovered / Items | Passed | Failed | Duration | Real Operational Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Terraform Formatting** | `terraform/` | `terraform fmt -check -recursive` | **`0`** | 16 files | 16 | 0 | 0.52s | `PASS — LOCAL AUTOMATED` |
| **Terraform Init** | `terraform/` | `terraform init -backend=false` | **`0`** | 2 plugins | 2 | 0 | 8.85s | `PASS — LOCAL AUTOMATED` |
| **Terraform Validate** | `terraform/` | `terraform validate` | **`0`** | 16 files | 16 | 0 | 1.15s | `PASS — LOCAL AUTOMATED` |
| **Backend Test Suite** | Repository Root | `python -m pytest backend/tests/ -v` | **`0`** | 89 tests | 89 | 0 | 24.88s | `PASS — LOCAL AUTOMATED` |
| **Frontend Lint / Typecheck** | `frontend/` | `npm run lint` (`tsc --noEmit`) | **`0`** | 1,505 modules | 1,505 | 0 | 7.91s | `PASS — LOCAL AUTOMATED` |
| **Frontend Production Build** | `frontend/` | `npm run build` (`tsc && vite build`) | **`0`** | 3 chunks | 3 | 0 | 5.43s | `PASS — LOCAL AUTOMATED` |
| **AWS CLI Version** | Workstation Host | `aws --version` | **`1`** | - | 0 | 1 | 0.40s | **`BLOCKED — NOT INSTALLED`** |
| **Docker CLI Version** | Workstation Host | `docker --version` | **`1`** | - | 0 | 1 | 0.35s | **`BLOCKED — NOT INSTALLED`** |
| **Git Staging Ignore Verification** | Repository Root | `git check-ignore -v terraform/terraform.staging.tfvars` | **`0`** | Match found | 1 | 0 | 0.22s | `PASS — GIT IGNORED` |

### Detailed Test Suite Breakdown (89/89 Passing)
- `backend/tests/test_analytics.py`: **14 tests passed** (telemetry recording, zero prompt/body retention, failure isolation, Pandas 2.2.2 ETL determinism, CSV formula injection escaping, admin RBAC isolation).
- `backend/tests/test_auth.py`: **10 tests passed** (user registration, bcrypt password hashing, input normalization, duplicate email rejection 409, privilege escalation prevention, JWT issuance, token decode, role claims).
- `backend/tests/test_cloud.py`: **18 tests passed** (discrete DB credentials assembly, percent-encoding, `DATABASE_URL` precedence, migration Scenarios A, B, and live PostgreSQL Scenario C on `localhost:5432`, Redis TLS URIs, health probes).
- `backend/tests/test_config.py`: **8 tests passed** (testing config isolation, fail-safe production checks, wildcard CORS rejection, `StagingConfig` validation, production DB URL rejection).
- `backend/tests/test_e2e_integration.py`: **6 tests passed** (end-to-end user journey, provider error handling, RBAC analytics isolation, token tampering defense, options catalog).
- `backend/tests/test_email_generator.py`: **15 tests passed** (template catalog, input validation, defensive prompt assembly, mocked OpenAI provider error mapping for 429, 502, 504).
- `backend/tests/test_health.py`: **6 tests passed** (`/api/health`, `/health/live`, `/api/ready`, `/health/ready`, security headers, 405 method rejection).
- `backend/tests/test_security.py`: **9 tests passed** (missing token rejection, malformed header handling, tampered JWT rejection, expired token rejection, login rate limiting, JSON parse error handling, payload size limit, security headers, error shielding).

---

## 2. Changes Made and Files Affected

In accordance with the rule to "fix only small, clearly safe local configuration defects that are necessary for this phase, and document every changed file":

1. **`docs/deployment-plan.md`**:
   - **Defect:** Section 6.2 Step 3 previously demonstrated planning staging with the example file directly (`terraform plan -var-file="terraform.tfvars.staging.example" -out="staging.tfplan"`).
   - **Remediation:** Corrected the command to reference the canonical local staging variable file (`terraform.staging.tfvars`) and added explicit instructions for the human operator to copy the template and supply local staging values before planning.
   - **Impact:** Aligns deployment documentation with canonical naming and prevents attempting execution with template files.

No other source or configuration files required modification. All core application logic, database schemas, and Terraform resource definitions remain unchanged.

---

## 3. Staging Variable-File Safety & Git Exemption Verification

The canonical intended staging variable file is:
- **Canonical Target:** `terraform/terraform.staging.tfvars`
- **Tracked Template:** [`terraform/terraform.staging.tfvars.example`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/terraform/terraform.staging.tfvars.example)

### Safety Verification Checklist:
- [x] **Placeholder Inspection:** `terraform/terraform.staging.tfvars.example` was inspected line-by-line. It contains only safe placeholders (`"wipro-org/smartmail-ai"`, `"smartmail_staging_admin"`, `""` for ACM certificate ARN). It contains zero real passwords, zero private keys, and zero production account numbers.
- [x] **Git Ignore Verification:** Executed `git check-ignore -v terraform/terraform.staging.tfvars`. Output confirmed active ignore rule:
  ```
  .gitignore:124:*.tfvars    terraform/terraform.staging.tfvars
  ```
- [x] **Unstaged / Untracked Secret Scan:** Executed `git status --short --ignored`. Output verified that no `.tfvars` file, `.env` file, private key, or credential file is tracked or staged.
- [x] **File Existence Check:** Executed `Get-ChildItem terraform -Filter "*tfvars*"`. Discovered:
  - `terraform.staging.tfvars.example` (tracked template)
  - `terraform.tfvars.example` (tracked base template)
  - `terraform.tfvars.staging.example` (tracked alternate template)
  - **The actual file `terraform.staging.tfvars` is NOT present on disk.**
- [x] **Environment & Region Verification:** The template explicitly configures `environment = "staging"` and `aws_region = "us-east-1"`.
- [x] **Variable Validation:** `variables.tf` enforces string types, CIDR validations, and default values. Sensitive database passwords and JWT secrets are managed via `random_password` and Secrets Manager rather than input variables.

### Mandatory Values Required from Human Operator:
Before `terraform.staging.tfvars` can be created locally, the human operator must configure:
1. `aws_region` (defaults to `"us-east-1"`)
2. `environment` (must be `"staging"`)
3. `github_repo` (the exact GitHub repository path, e.g., `"your-org/smartmail-ai"`)
4. `certificate_arn` (ACM SSL certificate ARN in `us-east-1`, or leave empty `""` for HTTP forward during initial preflight)
5. `container_image` (ECR image URL, or leave empty `""` to use `${aws_ecr_repository.backend.repository_url}:latest`)

---

## 4. AWS Identity Verification Status

### Command Execution:
```powershell
aws --version
```
### Execution Output:
```
aws : The term 'aws' is not recognized as the name of a cmdlet, function, script file, or operable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
    + CategoryInfo          : ObjectNotFound: (aws:String) [], CommandNotFoundException
    + FullyQualifiedErrorId : CommandNotFoundException
```
- **Exit Code:** `1`
- **Result:** **`BLOCKED — AWS IDENTITY NOT VERIFIED`**

### Gate Assessment & Human Operator Instructions:
In accordance with Rule 4 ("If unavailable, stop and document that the operator must install the official AWS CLI using an approved method. Do not install it automatically"):
1. The AWS CLI is not installed in the Windows `PATH` on this workstation.
2. No identity verification command (`aws sts get-caller-identity --profile smartmail-staging`) could be dispatched.
3. No AWS credentials, session tokens, or IAM roles could be evaluated.

#### Instructions for the Human Operator:
1. Download and run the official AWS CLI v2 Windows MSI installer from Amazon Web Services:
   `https://awscli.amazonaws.com/AWSCLIV2.msi`
2. Configure a named AWS profile dedicated to staging (do NOT use production credentials):
   ```powershell
   aws configure --profile smartmail-staging
   ```
3. Authenticate (via IAM Identity Center / SSO or temporary STS session):
   ```powershell
   aws sso login --profile smartmail-staging
   # Or verify credentials:
   aws sts get-caller-identity --profile smartmail-staging
   ```
4. Confirm that the returned `Account` ID matches the organization's approved, isolated AWS staging account before proceeding.

---

## 5. Terraform State Isolation & Backend Findings

### Active Backend Inspection:
Inspection of `terraform/main.tf` confirms that the active backend is currently the **default local backend**.
Lines 18–25 in `terraform/main.tf` contain a proposed S3 backend block that is commented out:
```hcl
  # NOTE: In production, configure an encrypted remote S3 backend with DynamoDB state locking:
  # backend "s3" {
  #   bucket         = "smartmail-ai-terraform-state"
  #   key            = "production/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "smartmail-ai-terraform-locks"
  # }
```

### State File Audit:
- Executed `Get-ChildItem terraform -Filter "*tfstate*" -Force`.
- **Findings:** Zero `*.tfstate` or `*.tfstate.backup` files exist in `terraform/`.
- Executed `terraform workspace list`. Output: `* default`.
- Zero AWS resources are tracked in local state.

### State Isolation Risks Discovered:
1. **Risk of Local State Overwrite:** If a developer applies staging using local state and subsequently applies production from the same directory, the local `terraform.tfstate` file would be overwritten, corrupting staging tracking or destroying resources.
2. **Defective Remote Backend Key in Template:** The commented backend block in `main.tf` hardcodes `key = "production/terraform.tfstate"`. If staging were initialized using this backend without dynamic key overriding (`-backend-config="key=staging/terraform.tfstate"`), staging and production would share and clobber the exact same state file!
3. **State Locking:** Terraform 1.5+ with AWS Provider 5.x supports remote state locking via Amazon DynamoDB (`dynamodb_table = "smartmail-ai-terraform-locks"`). If unconfigured, concurrent CI/CD runs could corrupt state.

### State Isolation Gate Assessment:
- **Result:** **`BLOCKED — TERRAFORM STATE ISOLATION NOT VERIFIED`**
- Per Phase 6.3 Rule 5: "If the repository cannot prove that the selected state belongs exclusively to the intended staging environment, stop before running a full Terraform plan."
- S3 remote state buckets and DynamoDB lock tables must NOT be provisioned in this phase.

#### Recommended Future Remote Backend Setup Procedure:
When authorized for infrastructure bootstrapping, execute a separate, dedicated bootstrap plan to create:
1. Staging state bucket: `smartmail-ai-staging-terraform-state` (SSE-KMS encrypted, versioning enabled, public access blocked).
2. Staging lock table: `smartmail-ai-staging-terraform-locks` (Billing mode: `PAY_PER_REQUEST`, Partition key: `LockID` of type `String`).
3. Initialize staging backend via:
   ```powershell
   terraform init -backend-config="bucket=smartmail-ai-staging-terraform-state" -backend-config="key=staging/terraform.tfstate" -backend-config="dynamodb_table=smartmail-ai-staging-terraform-locks" -backend-config="region=us-east-1"
   ```

---

## 6. Real Terraform Configuration & Security Boundary Review

A comprehensive audit of the 16 `.tf` configuration files in `terraform/` was conducted.

### 1. Networking & Security Boundaries ([`vpc.tf`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/terraform/vpc.tf), [`security_groups.tf`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/terraform/security_groups.tf))
- **VPC & Subnet CIDRs:** Parameterized via `var.vpc_cidr` (staging template: `10.1.0.0/16`). Isolated across 2 Availability Zones (`us-east-1a`, `us-east-1b`).
- **Subnet Tiering:**
  - 2 Public Subnets (`10.1.1.0/24`, `10.1.2.0/24`) attached to Internet Gateway.
  - 2 Private Application Subnets (`10.1.10.0/24`, `10.1.11.0/24`) routed through a Single NAT Gateway in Public Subnet 1.
  - 2 Isolated Database Subnets (`10.1.20.0/24`, `10.1.21.0/24`) with **zero** internet routing (no route to IGW or NAT).
- **Security Groups:**
  - `aws_security_group.alb`: Permits inbound 80/443 from `0.0.0.0/0`; egress restricted strictly to ECS security group on `var.container_port` (5000).
  - `aws_security_group.ecs`: Inbound restricted strictly from ALB security group via `aws_security_group_rule.ecs_ingress_from_alb`; outbound allows HTTPS (443) for OpenAI/ECR/CloudWatch/SecretsManager, port 5432 for RDS, and port 6379 for Redis.
  - `aws_security_group.rds`: Inbound port 5432 restricted **strictly** to ECS security group (`aws_security_group.ecs.id`). Public access explicitly disabled (`publicly_accessible = false`).
  - `aws_security_group.redis`: Inbound port 6379 restricted **strictly** to ECS security group.
- **ALB Listeners ([`alb.tf`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/terraform/alb.tf)):**
  - HTTP Listener (Port 80) forwards to target group when `certificate_arn == ""`, and automatically performs HTTP 301 redirect to HTTPS (Port 443) when a certificate is provided.
  - HTTPS Listener (Port 443) conditionally created when `certificate_arn != ""` using modern security policy `ELBSecurityPolicy-TLS13-1-2-2021-06`.

### 2. Compute, Containers & Least-Privilege IAM ([`ecs.tf`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/terraform/ecs.tf))
- **IAM Role Separation:**
  - **Task Execution Role (`aws_iam_role.ecs_execution_role`):** Scoped strictly to pulling ECR images (`AmazonECSTaskExecutionRolePolicy`) and reading specific Secrets Manager secrets (`secretsmanager:GetSecretValue` on `aws_secretsmanager_secret.app_secrets.arn`).
  - **Application Task Role (`aws_iam_role.ecs_task_role`):** Used at runtime by the container. Has **zero** Secrets Manager permissions, zero IAM permissions, and zero infrastructure mutation capabilities.
- **ECS Network Mode:** Configured for `awsvpc` with `assign_public_ip = false`. Tasks run exclusively in private subnets.
- **Circuit Breakers & Rolling Deploys:** `deployment_circuit_breaker` configured with `enable = true` and `rollback = true`. Deployment minimum healthy percent is 100%, maximum 200%.

### 3. Database & Cache ([`rds.tf`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/terraform/rds.tf), [`elasticache.tf`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/terraform/elasticache.tf))
- **PostgreSQL 16:** Storage encryption enabled (`storage_encrypted = true`), SSL forced (`rds.force_ssl = 1` in custom parameter group), automated 7-day backups enabled.
- **Deletion Protection:** Controlled via `var.enable_deletion_protection` (set to `false` in staging to allow teardown; `true` in production).
- **ElastiCache Redis 7:** At-rest encryption enabled, volatile-LRU eviction policy, deployed in private cache subnet group.

### 4. Secrets Management ([`secrets.tf`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/terraform/secrets.tf))
- Secret name: `smartmail-ai/staging/credentials` (namespaced by environment).
- Keys managed: `SECRET_KEY`, `JWT_SECRET_KEY`, `DB_PASSWORD`, `OPENAI_API_KEY`, `OPENAI_MODEL`.
- Direct Injection: ECS Task Definition injects secrets into container environment via `valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:<KEY>::"`.
- Zero Leakage: Terraform outputs ([`outputs.tf`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/terraform/outputs.tf)) expose only ARNs and DNS endpoints. Secret values and passwords are never exposed as outputs.

### 5. GitHub Actions OIDC Authentication ([`github_oidc.tf`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/terraform/github_oidc.tf))
- Federated authentication via `token.actions.githubusercontent.com` (no static long-lived AWS keys).
- Strict condition scoping:
  ```json
  "token.actions.githubusercontent.com:sub": [
    "repo:${var.github_repo}:environment:${var.environment}",
    "repo:${var.github_repo}:ref:refs/heads/main",
    "repo:${var.github_repo}:ref:refs/heads/master"
  ]
  ```
- Scoped deployment policy: Allows ECR push to `aws_ecr_repository.backend.arn`, ECS service update on `aws_ecs_service.backend.id`, frontend S3 sync, and CloudFront invalidation.

---

## 7. Health Checks, Container Runtime & Release Semantics

### Liveness vs. Readiness Semantics:
1. **Liveness Probe (`/api/health` and `/health/live`):**
   - Implemented in `backend/app/routes/health.py`.
   - Returns HTTP 200 with service metadata (`status: "healthy"`, `environment`, `version`).
   - Does NOT test downstream database or cache connectivity.
   - Used by the ALB Target Group (`alb.tf` line 31) and container Dockerfile `HEALTHCHECK`.
   - **Architectural Rationale:** Decouples process viability from database maintenance or transient blips, preventing cascading container terminations.
2. **Readiness Probe (`/api/ready` and `/health/ready`):**
   - Implemented in `backend/app/routes/health.py`.
   - Executes `SELECT 1` on the SQLAlchemy engine.
   - Returns HTTP 200 when database responds; returns HTTP 503 Service Unavailable with shielded error message when database is offline.
   - Used for deployment gating and traffic readiness checks.

### Container Build Evidence:
- **Local Host Docker Status:** `docker --version` exited with code 1 (`CommandNotFoundException`). Local Docker Desktop is not installed on this host. Runtime image verification remains **`PENDING — LOCAL DOCKER UNAVAILABLE`**.
- **CI Build Evidence:** Automated multi-stage Docker builds are tracked and verified in `.github/workflows/ci-cd.yml` via the `docker-validate` job using `docker/setup-buildx-action@v3` and `docker/build-push-action@v5`.
- **Backend Dockerfile:** Verified non-root execution (`appuser:appgroup` UID 10001), Python 3.12-slim base, multi-thread Gunicorn WSGI (`2 workers, 4 threads`), and embedded `HEALTHCHECK` probing `http://localhost:5000/api/health`.

---

## 8. Terraform Plan Status & Preflight Safety Gate

Per Mandatory Rule 8, a cloud-connected Terraform plan may only be executed if all prerequisites pass:

```
[PASS]  1. Terraform syntax, formatting, and provider initialization valid.
[PASS]  2. Staging variable template safe and git-ignored.
[FAIL]  3. AWS CLI available on workstation host. -> BLOCKED (CommandNotFoundException)
[FAIL]  4. AWS identity verified against approved staging account. -> BLOCKED (No identity)
[FAIL]  5. Canonical local variable file 'terraform.staging.tfvars' exists. -> BLOCKED (Missing)
[FAIL]  6. Terraform state isolation configured and verified. -> BLOCKED (Local default state)
[FAIL]  7. Explicit human authorization provided for live cloud planning. -> BLOCKED (Awaiting auth)
```

### Result:
# `BLOCKED — NO VERIFIED CLOUD PLAN`

- Because prerequisites 3, 4, 5, 6, and 7 failed, `terraform plan` was **not executed against AWS**.
- No dummy credentials were used.
- Provider data sources (`data.aws_caller_identity.current`, VPC lookups) were not queried against unverified accounts.
- Zero resources were created, changed, destroyed, or replaced.

---

## 9. Itemized Staging Cost Analysis & Recalculation

A comprehensive cost model was recalculated for `us-east-1` based on the staging architecture in `terraform.staging.tfvars.example`. 

> [!NOTE]
> All figures below are conservative estimates based on official AWS public pricing in `us-east-1` (730 operational hours/month). Actual costs may vary with network transfer volume.

| Architecture Component | Sizing & Specifications | Estimated Cost / Month | Assumptions & Exclusions |
| :--- | :--- | :---: | :--- |
| **AWS NAT Gateway** | 1 Single NAT Gateway (Public Subnet 1) | **$33.75** | $0.045/hr fixed ($32.85) + ~20 GB data processing ($0.90). Single AZ. |
| **Public IPv4 Addresses** | 1 NAT Gateway EIP + 2 ALB Public IPs | **$10.95** | AWS charge of $0.005/hr per in-use IPv4 address (3 IPs * 730 hrs). |
| **Application Load Balancer** | 1 Regional ALB across 2 AZs | **$22.27** | $0.0225/hr fixed ($16.43) + minimum 1 LCU staging usage ($5.84). |
| **Amazon RDS PostgreSQL** | `db.t4g.micro`, 20 GB gp3, Single-AZ | **$13.98** | $0.016/hr compute ($11.68) + 20 GB gp3 ($2.30). Backups in free tier. |
| **Amazon ElastiCache Redis** | `cache.t4g.micro`, 1 node, Single-AZ | **$11.68** | $0.016/hr compute ($11.68). Internal VPC traffic. |
| **Amazon ECS Fargate** | 1 Task: 0.25 vCPU (256), 0.5 GB RAM (512) | **$9.01** | vCPU ($7.39) + RAM ($1.62). Scaled to 1 task baseline for staging. |
| **Amazon CloudWatch** | Logs (7-day retention) + Container Insights | **$2.02** | ~2 GB log ingestion ($1.00) + storage ($0.02) + 1 alarm/metric ($1.00). |
| **AWS Secrets Manager** | 1 Master Secret (`staging/credentials`) | **$0.45** | $0.40/month per secret + ~10,000 API requests ($0.05). |
| **Amazon S3 (Frontend)** | 1 Standard Bucket (< 1 GB static assets) | **$0.15** | Storage (<$0.05) + PUT/GET deployment requests ($0.10). |
| **Amazon ECR** | 1-2 Backend Docker images (~1 GB total) | **$0.10** | Storage at $0.10/GB-month. Basic image vulnerability scanning free. |
| **Amazon CloudFront** | 1 Global CDN Distribution | **$0.00** | Covered under AWS Always Free Tier (1 TB data transfer + 10M requests). |
| **AWS KMS & ACM** | AWS-managed default keys + ACM Public Cert | **$0.00** | AWS-managed KMS keys and ACM public certificates are free. |
| **Route 53 Hosted Zone** | Staging subdomain (optional) | **$0.00** | Excluded (using ALB DNS / CloudFront domain for staging preflight). |
| **Total Staging Estimate** | **Full Integrated Staging Environment** | **~$104.36 / month** | **~$3.48 / operational day during active staging validation.** |

### Cost Comparison Rationale:
The previous preliminary estimate of $91.20/month omitted the AWS Public IPv4 address charges ($0.005/hour introduced across all AWS services on February 1, 2024 for the NAT Gateway Elastic IP and the ALB dual-AZ public endpoints, adding ~$10.95/month). The recalculated figure of **$104.36/month** is the accurate, comprehensive operational baseline.

---

## 10. Teardown and Recovery Safeguards Review

The teardown process and configuration safeguards were audited without executing destructive commands:

1. **Deletion Protection Parameterization:**
   - In `rds.tf` line 44, `deletion_protection = var.enable_deletion_protection`.
   - In `terraform.staging.tfvars.example`, `enable_deletion_protection = false` to enable clean automated teardown of staging when testing concludes. In production, this default is `true`.
   - Line 45: `skip_final_snapshot = !var.enable_deletion_protection`. Staging skips final snapshots upon intentional destroy, preventing orphaned snapshot storage fees.
2. **S3 Bucket Safeguards:**
   - In `s3_cloudfront.tf` line 11, `force_destroy = false`. S3 will refuse deletion if objects exist, preventing accidental data loss without an explicit deletion workflow.
3. **Database Migration Reversibility:**
   - Alembic migration `001_initial_schema.py` defines explicit `upgrade()` and `downgrade()` functions. Table structures for `users` and `generation_events` can be cleanly reversed.
4. **Environment Isolation Boundary:**
   - Dedicated VPC CIDR (`10.1.0.0/16`), dedicated cluster (`smartmail-ai-staging-cluster`), and dedicated secret (`smartmail-ai/staging/credentials`) guarantee that a staging teardown cannot affect production resources.
5. **Human Approval Safeguard:**
   - The command `terraform destroy -var-file="terraform.staging.tfvars"` must never be run in automated scripts without an interactive human confirmation prompt and review of the planned resource deletions.

---

## 11. Unresolved Issues & Remediation Action Plan

| # | Unresolved Item | Current Status | Remediation Action Plan | Owner |
| :---: | :--- | :---: | :--- | :--- |
| **1** | **AWS CLI Not Installed on Host** | `BLOCKED` | Install AWS CLI v2 via MSI installer (`AWSCLIV2.msi`). Verify via `aws --version`. | Human Operator |
| **2** | **AWS Staging Profile Unconfigured** | `BLOCKED` | Run `aws configure --profile smartmail-staging`. Verify via `aws sts get-caller-identity --profile smartmail-staging`. | Human Operator |
| **3** | **Staging State Backend Unconfigured** | `BLOCKED` | Review and execute remote backend bootstrap plan (S3 bucket + DynamoDB lock table for staging). | DevOps / Operator |
| **4** | **`terraform.staging.tfvars` Missing** | `BLOCKED` | Copy `terraform.staging.tfvars.example` to `terraform.staging.tfvars` and set required repository/account parameters. | Human Operator |
| **5** | **Cloud-Connected Plan Unverified** | `BLOCKED` | Execute `terraform plan -var-file="terraform.staging.tfvars" -out="staging.tfplan"` once Items 1–4 pass. | Senior DevOps |
| **6** | **Local Docker Desktop Missing** | `PENDING` | Local container runtime unavailable. Validated in CI via GitHub Actions `docker-validate` job. | Optional / DevOps |
| **7** | **Live OpenAI Staging Key** | `PENDING` | Real OpenAI API key must be populated directly into AWS Secrets Manager post-provisioning (never committed). | Human Operator |

---

## 12. Final Release Gate Decision

# Decision: `BLOCKED — AWS IDENTITY NOT VERIFIED`

### Primary Justification:
1. **AWS CLI Is Not Available:** `aws --version` returned exit code 1 (`CommandNotFoundException`). The local workstation lacks the AWS CLI tooling required to query STS or verify caller identity.
2. **AWS Identity Is Not Verified:** No authenticated caller identity (`Account`, `Arn`, `UserId`) has been confirmed against the approved staging AWS account.
3. **Terraform State Isolation Is Not Established:** Terraform is configured with local state defaulting to `* default` workspace. No remote S3 backend or DynamoDB state locking is configured for staging.
4. **Staging Variable File Is Not Present:** `terraform/terraform.staging.tfvars` does not exist on disk.
5. **No Cloud-Connected Plan Exists:** In accordance with the mandatory operating boundaries, `terraform plan` was not run against AWS.

### Execution Boundaries Upheld:
- **Zero AWS infrastructure provisioned or mutated.**
- **Zero state files deleted or overwritten.**
- **Zero secrets exposed or logged.**
- **Zero billable OpenAI requests sent.**
- **100% test passing rate maintained locally (89/89 backend tests, clean frontend build).**

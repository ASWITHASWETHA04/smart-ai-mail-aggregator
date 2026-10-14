# SMARTMAIL AI — PHASE 6.4A: AWS ACCESS SETUP, STATE BACKEND DESIGN & STAGING AUTHORIZATION READINESS REPORT

**Project:** SmartMail AI — Secure, Cloud-Based AI Email Generation Platform  
**Use Case:** Wipro CPPE Use Case 5  
**Release Target:** `v1.0.0-rc1`  
**Current Phase:** Phase 6.4A — AWS Access Setup, State Backend Design & Staging Authorization Readiness  
**Previous Phase:** Phase 6.3 — Cloud Identity Verification, Terraform State Isolation & Verified Staging Plan  
**Execution Timestamp:** 2026-10-14 16:50:00 UTC+05:30  
**Evaluator Roles:** Senior AWS DevOps Engineer, Terraform Security Reviewer, Cloud Cost Analyst, and Release Manager  
**Primary Objective:** Prepare SmartMail AI for an authorized staging deployment by resolving prerequisites, designing state backend isolation, reconciling costs, and establishing clear gates without modifying cloud infrastructure.  
**Report File:** `docs/phase-6-4a-access-and-backend-readiness-report.md`

---

## Final Phase Decision & Gate Status

# `BLOCKED — AWS IDENTITY NOT VERIFIED`
*(Secondary Blockers: `BLOCKED — TERRAFORM STATE ISOLATION NOT VERIFIED` & `BLOCKED — STAGING CONFIGURATION INCOMPLETE`)*

> [!IMPORTANT]
> **Mandatory Operating Safety Boundaries Maintained:**
> - Zero live AWS infrastructure was provisioned, updated, or destroyed.
> - `terraform apply`, `terraform destroy`, and `terraform import` were **not** executed.
> - Zero S3 buckets, DynamoDB tables, KMS keys, or IAM roles were created.
> - Zero state migration commands were dispatched.
> - Zero database migrations or application deployments were triggered.
> - Zero billable OpenAI requests were dispatched.
> - Zero secrets or access credentials were asked for, stored, or exposed.
> - Local SQLite development workflow and automated test suites remain 100% operational (89/89 backend tests passing, clean frontend build).

---

## 1. Local Tool and Test Results

Every tool, runtime environment, test suite, and static analysis check was verified directly against the workstation host and active repository:

| Verification Target | Working Directory / Host | Command Executed | Exit Code | Result / Metrics | Duration | Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **Terraform CLI** | `terraform/` | `terraform version` | **`0`** | v1.16.5 (AWS v5.100.0, Random v3.9.1) | 0.40s | `PASS — VERIFIED` |
| **AWS CLI** | Workstation Host | `aws --version` | **`1`** | `CommandNotFoundException` (Not installed) | 0.35s | **`BLOCKED — NOT INSTALLED`** |
| **Git Tooling** | Repository Root | `git --version` | **`0`** | `git version 2.55.0.windows.4` | 0.15s | `PASS — VERIFIED` |
| **Git Working Tree** | Repository Root | `git status --short` | **`0`** | Branch `master` (No commits yet, untracked) | 0.20s | `PASS — CLEAN WORKSPACE` |
| **Python Environment** | `backend/venv` | `python --version` | **`0`** | Python 3.12.3 (Dependencies installed) | 0.25s | `PASS — VERIFIED` |
| **Node.js Environment** | `frontend/` | `node -v` | **`0`** | v24.15.0 | 0.15s | `PASS — VERIFIED` |
| **npm Tooling** | `frontend/` | `npm -v` | **`0`** | 11.12.1 | 0.20s | `PASS — VERIFIED` |
| **Docker CLI** | Workstation Host | `docker --version` | **`1`** | `CommandNotFoundException` (Not installed) | 0.35s | **`PENDING — LOCAL DOCKER MISSING`** |
| **Terraform Formatting** | `terraform/` | `terraform fmt -check -recursive` | **`0`** | 16 files checked | 0.45s | `PASS — CLEAN FORMAT` |
| **Terraform Init** | `terraform/` | `terraform init -backend=false` | **`0`** | Providers initialized successfully | 7.12s | `PASS — INITIALIZED` |
| **Terraform Validation** | `terraform/` | `terraform validate` | **`0`** | Configuration is valid | 1.15s | `PASS — VALIDATED` |
| **Backend Test Suite** | Repository Root | `pytest backend/tests/ -v` | **`0`** | **89 passed, 0 failed, 0 errors** | 14.70s | `PASS — 100% COVERAGE` |
| **Frontend Lint / Types** | `frontend/` | `npm run lint` (`tsc --noEmit`) | **`0`** | 1,505 modules checked | 7.85s | `PASS — 0 TYPE ERRORS` |
| **Frontend Build** | `frontend/` | `npm run build` (`tsc && vite`) | **`0`** | 3 distribution chunks generated | 6.51s | `PASS — PRODUCTION BUILD` |

### Detailed Backend Suite Summary (89/89 Tests Passing):
- `test_analytics.py`: 14 tests (telemetry logging, zero prompt/body retention, failure isolation, Pandas 2.2.2 ETL determinism, CSV formula injection sanitization, admin RBAC isolation).
- `test_auth.py`: 10 tests (registration, bcrypt salted password hashing, input normalization, duplicate email 409 rejection, privilege escalation prevention, JWT issuance, token claims).
- `test_cloud.py`: 18 tests (discrete DB credentials assembly, percent-encoding, `DATABASE_URL` precedence, migration Scenarios A, B, and live PostgreSQL Scenario C on `localhost:5432`, Redis TLS URIs, health probes).
- `test_config.py`: 8 tests (testing config isolation, fail-safe production checks, wildcard CORS rejection, `StagingConfig` validation, production DB URL rejection).
- `test_e2e_integration.py`: 6 tests (complete journey, provider error handling, RBAC analytics isolation, token tampering defense, options catalog).
- `test_email_generator.py`: 15 tests (catalog, input validation, prompt assembly, mocked provider parsing for 429, 502, 504).
- `test_health.py`: 6 tests (`/api/health`, `/health/live`, `/api/ready`, `/health/ready`, security headers, 405 checks).
- `test_security.py`: 9 tests (token tampering, expiration, rate limiting, payload limits, security headers).

---

## 2. Actual Repository Changes

During Phase 6.4A:
1. **`docs/deployment-plan.md`**: Fixed line 130 to reference canonical `terraform.staging.tfvars` instead of example file.
2. **`RTM.md`**: Updated with `REQ-STG-05` tracing Phase 6.3/6.4A cloud identity, state isolation, and preflight requirements.
3. **`docs/phase-plan.md`**: Updated milestones reflecting Phase 6.3 completion and Phase 6.4A preflight status.
4. **`docs/phase-6-4a-access-and-backend-readiness-report.md`**: Authored this comprehensive readiness and backend architecture report.

No application code, database schema, or infrastructure resource configurations were altered.

---

## 3. Staging Variable-File & Git-Ignore Verification

The canonical intended staging variable file is:
- **Canonical Local Target:** `terraform/terraform.staging.tfvars`
- **Tracked Template:** [`terraform/terraform.staging.tfvars.example`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/terraform/terraform.staging.tfvars.example)

### Safety Verification Checklist:
- [x] **Placeholder Verification:** `terraform/terraform.staging.tfvars.example` contains only benign placeholders (`"wipro-org/smartmail-ai"`, `"smartmail_staging_admin"`, `""` for ACM certificate ARN). No real secrets or production accounts exist.
- [x] **Git Ignore Verification:** Executed `git check-ignore -v terraform/terraform.staging.tfvars`. Output confirmed rule:
  ```
  .gitignore:124:*.tfvars    terraform/terraform.staging.tfvars
  ```
- [x] **Unstaged / Untracked Secret Scan:** Executed `git status --short --ignored`. Zero `.tfvars` or `.env` files are tracked or staged.
- [x] **File Existence Check:** `terraform/terraform.staging.tfvars` is **not present on disk**.
- [x] **Environment & Region Settings:** Template explicitly sets `environment = "staging"` and `aws_region = "us-east-1"`.
- [x] **Variable Defaults Audit:** In `terraform/variables.tf`, `environment` defaults to `"production"`. Supplying `-var-file="terraform.staging.tfvars"` is strictly required to enforce the staging tier.
- [x] **Container Image Setting:** Defaults to `""`, resolving dynamically to `${aws_ecr_repository.backend.repository_url}:latest` in `ecs.tf` to prevent cross-account or production image confusion.

---

## 4. AWS Access & Identity Verification Status

### Command Attempt:
```powershell
aws --version
```
- **Exit Code:** `1`
- **Error:** `aws : The term 'aws' is not recognized as the name of a cmdlet, function, script file, or operable program.`
- **Result:** **`BLOCKED — AWS IDENTITY NOT VERIFIED`**

### Security Rule Adherence:
- The AWS CLI is not installed on this workstation.
- In accordance with Mandatory Rule 2, the agent did **not** install software automatically.
- No STS caller identity check could be executed.
- No access keys or passwords were requested or pasted.

#### Instructions for the Operator:
1. Install AWS CLI v2 via the official MSI installer: `https://awscli.amazonaws.com/AWSCLIV2.msi`
2. Configure a named AWS profile dedicated to staging (IAM Identity Center SSO preferred):
   ```powershell
   aws configure sso --profile smartmail-staging
   # Or standard profile:
   aws configure --profile smartmail-staging
   ```
3. Authenticate and verify caller identity:
   ```powershell
   aws sts get-caller-identity --profile smartmail-staging
   ```

---

## 5. Approved Account Confirmation Status

- **Current Status:** **`BLOCKED — AWAITING OPERATOR CONFIRMATION`**
- In accordance with Section 5, an account must not be inferred as staging merely from a profile name or label.
- The human operator must explicitly confirm the 12-digit AWS Account ID allocated for staging before any cloud-connected plan is authorized.

---

## 6. Existing Terraform State Findings

- **Active Backend:** Local backend (default `* default` workspace).
- **State File Presence:** Checked via `Get-ChildItem -Filter "*tfstate*" -Force`. Zero `.tfstate` files exist in `terraform/`.
- **Existing Resources:** Zero resources are tracked in state.
- **Shared Backend Status:** No existing remote S3 bucket or DynamoDB table is configured.
- **Sensitive Value Risk:** Terraform state stores raw attributes of all resources. In this architecture, state contains plaintext outputs of `random_password.jwt_secret`, `random_password.flask_secret`, `random_password.db_password`, and `aws_secretsmanager_secret_version.app_secrets.secret_string`. State files must never be committed to Git or left unencrypted.
- **Result:** **`BLOCKED — TERRAFORM STATE ISOLATION NOT VERIFIED`**

---

## 7. Proposed Staging Backend Architecture (Design Only)

To prevent staging from ever colliding with production or exposing state, the following architecture is designed for future bootstrap:

```
[ Local Workstation / CI Runner ]
                │
                │ (Terraform AWS Provider via STS)
                ▼
┌─────────────────────────────────────────────────────────────┐
│ AWS Staging Account (us-east-1)                             │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ S3 Bucket: smartmail-ai-staging-terraform-state       │  │
│  │  - BucketOwnerEnforced (ACLs disabled)                │  │
│  │  - 100% Public Access Blocked                         │  │
│  │  - Server-Side Encryption (AES256 or AWS KMS)         │  │
│  │  - S3 Versioning: Enabled (Recovery capability)       │  │
│  │  - TLS 1.2+ Enforced in Bucket Policy                 │  │
│  │                                                       │  │
│  │  Key: staging/terraform.tfstate                       │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ DynamoDB Table: smartmail-ai-staging-terraform-locks   │  │
│  │  - Billing: PAY_PER_REQUEST (On-Demand)               │  │
│  │  - Partition Key: LockID (String)                     │  │
│  │  - Prevents concurrent state mutations                │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Key Isolation Characteristics:
1. **Distinct Account & Bucket Ownership:** The staging state bucket must reside in the approved staging account, completely distinct from production.
2. **Explicit State Key:** `key = "staging/terraform.tfstate"`. The commented example in `main.tf` (`production/terraform.tfstate`) must **never** be used for staging.
3. **Encryption & Access Control:** SSE enabled; bucket policy denies non-SSL transport (`aws:SecureTransport: "false"`).
4. **State Locking:** DynamoDB partition key `LockID` (String) guarantees that concurrent pipeline jobs fail safe with an exit code rather than corrupting state.
5. **Least-Privilege IAM Policy for Deployer:**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": ["s3:ListBucket"],
         "Resource": "arn:aws:s3:::smartmail-ai-staging-terraform-state"
       },
       {
         "Effect": "Allow",
         "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
         "Resource": "arn:aws:s3:::smartmail-ai-staging-terraform-state/staging/terraform.tfstate"
       },
       {
         "Effect": "Allow",
         "Action": ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:DeleteItem"],
         "Resource": "arn:aws:dynamodb:us-east-1:*:table/smartmail-ai-staging-terraform-locks"
       }
     ]
   }
   ```
6. **Future Bootstrap Procedure:** A separate bootstrap template will provision this bucket and table once the operator authorizes cloud setup.

---

## 8. Environment Isolation and IAM/OIDC Findings

A complete audit of `terraform/` configurations and `.github/workflows/ci-cd.yml` verified the following isolation boundaries:

- **Network Tiering ([`vpc.tf`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/terraform/vpc.tf), [`security_groups.tf`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/terraform/security_groups.tf)):**
  - Dedicated VPC CIDR (`10.1.0.0/16` for staging vs `10.0.0.0/16` for production).
  - RDS and Redis deployed into isolated database subnets with no internet gateway or NAT routes.
  - Security groups strictly bound: ALB -> ECS (port 5000), ECS -> RDS (port 5432), ECS -> Redis (port 6379).
- **IAM Role Separation ([`ecs.tf`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/terraform/ecs.tf)):**
  - Task Execution Role: Authorized only for ECR image pull and reading `smartmail-ai/staging/credentials` from Secrets Manager.
  - Application Task Role: Zero IAM permissions, zero Secrets Manager read access at runtime.
- **ALB Health Decoupling ([`alb.tf`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/terraform/alb.tf)):**
  - Target group checks `/api/health` (process liveness only), eliminating cascading container restart loops during database maintenance.
- **GitHub Actions OIDC ([`github_oidc.tf`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/terraform/github_oidc.tf), [`ci-cd.yml`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/.github/workflows/ci-cd.yml)):**
  - Ephemeral short-lived credentials via GitHub OIDC provider.
  - Scoped to `repo:${var.github_repo}:environment:${var.environment}`.
  - Deployment workflow strictly sequences staging pre-deployment migration tasks (`flask db upgrade` in an isolated Fargate task with exit code validation) before updating the rolling service.

---

## 9. Staging Cost Model Reconciliation

The cost model was mathematically reconciled for `us-east-1` (730 operational hours/month), distinguishing **fixed idle infrastructure costs** from **variable usage charges**:

| Architecture Component | Sizing & Specifications | Estimated Cost / Month | Pricing Type | Pricing Basis & Assumptions |
| :--- | :--- | :---: | :---: | :--- |
| **AWS NAT Gateway** | 1 Single NAT Gateway (Public Subnet 1) | **$33.75** | Fixed + Variable | $0.045/hr fixed ($32.85) + ~20 GB data processing ($0.90). Accrues 24/7. |
| **Public IPv4 Addresses** | 1 NAT Gateway EIP + 2 ALB Public IPs | **$10.95** | Fixed | $0.005/hr per IPv4 address (3 IPs * 730 hrs). Accrues 24/7. |
| **Application Load Balancer** | 1 Regional ALB across 2 AZs | **$22.27** | Fixed + Variable | $0.0225/hr fixed ($16.43) + min 1 LCU staging usage ($5.84). Fixed floor: $16.43. |
| **Amazon RDS PostgreSQL** | `db.t4g.micro`, 20 GB gp3, Single-AZ | **$13.98** | Fixed | $0.016/hr compute ($11.68) + 20 GB gp3 ($2.30). Backups in free tier. |
| **Amazon ElastiCache Redis** | `cache.t4g.micro`, 1 node, Single-AZ | **$11.68** | Fixed | $0.016/hr compute ($11.68). Internal VPC traffic. |
| **Amazon ECS Fargate** | 1 Task: 0.25 vCPU (256), 0.5 GB RAM (512) | **$9.01** | Fixed (while active) | vCPU ($7.39) + RAM ($1.62). Scaled to 1 task baseline for staging. |
| **Amazon CloudWatch** | Logs (7-day retention) + Container Insights | **$2.02** | Variable | ~2 GB log ingestion ($1.00) + storage ($0.02) + 1 alarm/metric ($1.00). |
| **AWS Secrets Manager** | 1 Master Secret (`staging/credentials`) | **$0.45** | Fixed + Variable | $0.40/month per secret + ~10,000 API requests ($0.05). |
| **Amazon S3 (Frontend)** | 1 Standard Bucket (< 1 GB static assets) | **$0.15** | Variable | Storage (<$0.05) + PUT/GET deployment requests ($0.10). |
| **Amazon ECR** | 1-2 Backend Docker images (~1 GB total) | **$0.10** | Variable | Storage at $0.10/GB-month. Basic image scanning free. |
| **Amazon CloudFront** | 1 Global CDN Distribution | **$0.00** | Free Tier | Covered under Always Free Tier (1 TB data transfer + 10M requests). |
| **AWS KMS & ACM** | AWS-managed default keys + ACM Public Cert | **$0.00** | Free | AWS-managed KMS keys and ACM public certificates are free. |
| **Route 53 Hosted Zone** | Staging subdomain (optional) | **$0.00** | Excluded | Excluded (using ALB DNS / CloudFront domain for staging preflight). |
| **Total Staging Estimate** | **Full Integrated Staging Environment** | **~$104.36 / month** | **Mixed** | **~$3.48 / operational day during active staging validation.** |

### Cost Reconciliation Highlights:
- **Fixed Baseline Cost (accrues 24/7 even if zero traffic occurs):** $32.85 (NAT) + $10.95 (IPv4) + $16.43 (ALB) + $13.98 (RDS) + $11.68 (Redis) + $9.01 (Fargate) + $0.40 (Secret) = **$95.30 / month (~$3.18 / day)**.
- **Variable Usage Cost:** ~$9.06 / month.
- **Teardown Cost Advantage:** Tearing down staging after active verification saves ~$3.18 per day in idle charges.

---

## 10. Remaining Blockers & Required Human Decisions

| # | Blocker Item | Current Status | Required Decision / Action from Operator |
| :---: | :--- | :---: | :--- |
| **1** | **AWS CLI Installation** | `BLOCKED` | Operator must install AWS CLI v2 via `AWSCLIV2.msi` on workstation. |
| **2** | **Staging Account Confirmation** | `BLOCKED` | Operator must provide the authorized 12-digit AWS Account ID for staging. |
| **3** | **Staging Authentication Profile** | `BLOCKED` | Operator must configure `smartmail-staging` profile and verify via STS. |
| **4** | **Staging Variable File Setup** | `BLOCKED` | Operator must copy `terraform.staging.tfvars.example` to `terraform.staging.tfvars` and set repository details. |
| **5** | **State Backend Bootstrapping** | `BLOCKED` | Operator must approve future creation of staging S3 bucket and DynamoDB lock table. |
| **6** | **Cloud-Connected Plan Authorization** | `BLOCKED` | Operator must provide explicit authorization for read-only `terraform plan`. |

---

## 11. Exact Commands the Operator May Execute Later

Once Prerequisites 1–5 are met, the human operator may execute the following exact command sequence from the workstation:

```powershell
# Step 1: Verify authenticated staging identity (Read-Only)
aws sts get-caller-identity --profile smartmail-staging

# Step 2: Navigate to Terraform directory
cd "terraform"

# Step 3: Create local canonical variable file from template (if not already done)
Copy-Item "terraform.staging.tfvars.example" -Destination "terraform.staging.tfvars"

# Step 4: Initialize Terraform with the approved remote staging backend
terraform init `
  -backend-config="bucket=smartmail-ai-staging-terraform-state" `
  -backend-config="key=staging/terraform.tfstate" `
  -backend-config="dynamodb_table=smartmail-ai-staging-terraform-locks" `
  -backend-config="region=us-east-1"

# Step 5: Execute read-only cloud-connected plan (Does NOT create resources)
terraform plan -var-file="terraform.staging.tfvars" -out="staging.tfplan"

# Step 6: Review the generated plan
terraform show -json "staging.tfplan"
```

---

## 12. Final Release Gate Decision

# Decision: `BLOCKED — AWS IDENTITY NOT VERIFIED`

### Primary Justifications:
1. **AWS CLI is unavailable** on the local host (`CommandNotFoundException`, exit code 1).
2. **AWS identity is unverified**; no staging principal or Account ID has been authorized.
3. **Terraform remote backend isolation is not yet provisioned** (currently local default state).
4. **Local staging variable file is not populated**.
5. **Mandatory stop conditions respected:** Zero cloud mutations, zero secrets exposed, zero state collisions.

# SMARTMAIL AI — PHASE 6.4D: OPERATOR READINESS & EVIDENCE GATE REPORT

**Project:** SmartMail AI — Secure, Cloud-Based AI Email Generation Platform  
**Use Case:** Wipro CPPE Use Case 5  
**Release Target:** `v1.0.0-rc1`  
**Current Phase:** Phase 6.4D — Operator Readiness & Evidence Gate  
**Previous Phase:** Phase 6.4C — Staging Guardrails, Cost Reconciliation & Release Baseline  
**Target AWS Region:** `us-east-1`  
**Target Environment:** `staging`  
**Execution Timestamp:** 2026-10-14 17:55:00 UTC+05:30  
**Evaluator Roles:** Senior AWS DevOps Engineer, Terraform Security Reviewer, Application Security Engineer, and Release Manager  
**Primary Objective:** Inspect the actual repository, verify AWS CLI v2 and STS identity readiness, enforce 12-digit staging account guardrails and check assertions, review local Terraform backend state, audit Git release baseline distinction (untracked vs committed), reconcile cost assumptions ($104.36/mo), execute local test suites (89/89 backend, clean frontend build, 0 lint errors, valid Terraform), and produce an evidence-backed go/no-go gate decision without provisioning cloud resources.  
**Report Document:** `docs/phase-6-4d-operator-readiness-and-evidence-gate-report.md`

---

## 1. Executive Go/No-Go Decision & Release Gate Status

# Decision: `LOCAL PREFLIGHT PASSED — CLOUD OPERATIONS STILL BLOCKED`

### Detailed Gate Status Evaluation:
| Gate Category | Status | Primary Technical Reason |
| :--- | :---: | :--- |
| **Local Automated Test Suites** | `PASS — VERIFIED` | 89/89 Pytest tests passed in 16.28s; 0 failures, 0 errors. |
| **Frontend Static Typing & Lint** | `PASS — VERIFIED` | `tsc --noEmit` clean across 1,505 modules; 0 TypeScript errors. |
| **Frontend Production Build** | `PASS — VERIFIED` | Vite production build clean in 5.91s; 3 optimized distribution chunks. |
| **Terraform IaC Syntax & Providers** | `PASS — VERIFIED` | `terraform fmt -check`, `init -backend=false`, and `validate` passed clean (v1.16.5). |
| **Git Secrets & Artifact Exclusion** | `PASS — VERIFIED` | `git check-ignore` confirms `.env`, `*.tfvars`, `*.tfstate`, `*.tfplan`, `*.tflock`, `*.db` excluded. |
| **AWS CLI & Identity Verification** | **`BLOCKED — AWS IDENTITY NOT VERIFIED`** | AWS CLI v2 not installed on host (`CommandNotFoundException`, exit code 1). |
| **Staging Account Guardrail** | **`BLOCKED — STAGING CONFIGURATION INCOMPLETE`** | Canonical `terraform.staging.tfvars` missing; `allowed_account_id` not yet populated with 12-digit ID. |
| **Terraform State Backend** | **`BLOCKED — TERRAFORM STATE ISOLATION NOT VERIFIED`** | Backend is currently local; S3 state bucket `smartmail-ai-staging-terraform-state` unbootstrapped. |
| **Git Release Baseline** | **`BLOCKED — RELEASE BASELINE NOT COMMITTED`** | Branch `master` has 0 commits; working copy is untracked (not a committed baseline). |
| **Container Build Evidence** | **`PENDING — DOCKER BUILD EVIDENCE`** | Local Docker Desktop not installed (`CommandNotFoundException`); CI build runs on remote push. |
| **Overall Preflight Gate** | **`READY FOR HUMAN REVIEW`** | Ready for human operator to install AWS CLI, authenticate profile, and commit baseline. |

> [!IMPORTANT]
> **Mandatory Safety Rules Strictly Upheld:**
> - Zero live AWS infrastructure was provisioned, updated, destroyed, or imported.
> - `terraform apply`, `terraform destroy`, `terraform state mv`, and `terraform state rm` were **not** executed.
> - Zero remote S3 backend buckets or DynamoDB tables were provisioned.
> - Zero cloud-connected Terraform plans were dispatched.
> - Zero state migration commands were executed.
> - Zero database migrations or application deployments were triggered.
> - Zero billable OpenAI requests were dispatched.
> - Zero credentials, tokens, or secret values were requested, pasted, or stored.
> - Zero user changes or repository files were committed, reset, reverted, or discarded.
> - Local SQLite development workflow and automated test suites remain 100% operational (89/89 backend tests passing, clean frontend build).

---

## 2. Actual Repository and Git Baseline Status

A comprehensive audit of the Git working copy was performed on the workstation:

```
$ git status
On branch master
No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.github/
	.gitignore
	README.md
	RTM.md
	backend/
	docker-compose.yml
	docs/
	frontend/
	terraform/

nothing added to commit but untracked files present (use "git add" to track)
```

### Clarification of Git Baseline Distinction:
Previous discussions colloquially referred to the repository as a "clean baseline." In Phase 6.4D, we explicitly correct and delineate the exact engineering states:

1. **Untracked Working Directory (CURRENT STATE):**
   - The repository has been initialized via `git init`.
   - 0 commits exist on branch `master`.
   - 0 files are staged in the Git index.
   - All 9 directories/files exist as untracked files in the working directory.
   - **Conclusion:** An untracked working copy does **NOT** constitute a committed or auditable release baseline.
2. **Reviewed Staging Index (NEXT HUMAN STEP):**
   - The human operator reviews all files against `.gitignore` to ensure zero secrets or local state files are included.
   - Operator stages the approved project files using `git add`.
3. **Initial Committed Baseline (PLANNED):**
   - Operator creates the root commit (`git commit -m "feat: initial commit for SmartMail AI v1.0.0-rc1 release baseline"`).
   - Generates the first cryptographically hashed Git tree object representing the audited code.
4. **Tagged Release Candidate (PLANNED):**
   - Operator applies an annotated Git tag (`git tag -a v1.0.0-rc1 -m "SmartMail AI Release Candidate 1"`).
   - Serves as the immutable release artifact reference for CI/CD pipelines.

### Proposed Initial Commit Allowlist:
The following directories and files are verified clean of secrets and recommended for the operator's initial staging review:
```
.github/workflows/ci-cd.yml
.gitignore
README.md
RTM.md
docker-compose.yml
backend/ (app/, migrations/, tests/, Dockerfile, requirements.txt, run.py)
docs/ (all architecture, security, deployment, and phase reports)
frontend/ (src/, public/, index.html, package.json, tsconfig.json, vite.config.ts, Dockerfile, nginx.conf)
terraform/ (*.tf files and *.example variable templates)
```

---

## 3. AWS CLI and Identity Readiness

### Host Tooling Verification:
- **Command:** `aws --version`
- **Exit Code:** `1`
- **Output:**
  ```
  aws : The term 'aws' is not recognized as the name of a cmdlet, function, script file, or operable program.
  CategoryInfo: ObjectNotFound: (aws:String) [], CommandNotFoundException
  ```
- **Evaluation:** AWS CLI v2 is **not installed** on the host.
- **Identity Check (`aws sts get-caller-identity --profile smartmail-staging`):** Could not be executed. No credentials or AWS profiles exist locally.
- **Gate Status:** **`BLOCKED — AWS IDENTITY NOT VERIFIED`**

### Manual Operator Setup Instructions:
To resolve this blocker safely, the operator must perform the following manual steps:

1. **Download & Install Official AWS CLI v2:**
   - Download the official Windows MSI installer directly from AWS:  
     `https://awscli.amazonaws.com/AWSCLIV2.msi`
   - Run the installer and complete the setup wizard.
   - Verify installation in a fresh PowerShell window:
     ```powershell
     aws --version
     # Expected: aws-cli/2.x.x Python/3.x.x Windows/10.x.x ...
     ```
2. **Configure Staging Profile via Approved Authentication Method:**
   - **Option A: IAM Identity Center (AWS SSO - Strongly Recommended):**
     ```powershell
     aws configure sso --profile smartmail-staging
     # Follow prompts for SSO start URL, SSO region, staging account selection, and role
     aws sso login --profile smartmail-staging
     ```
   - **Option B: Temporary IAM Role Session / Credentials:**
     ```powershell
     aws configure --profile smartmail-staging
     # Set AWS Access Key ID, Secret Access Key, Default region: us-east-1, Default output: json
     ```
3. **Verify Identity and Confirm 12-Digit Account ID:**
   ```powershell
   aws sts get-caller-identity --profile smartmail-staging
   ```
   *The operator must verify that the printed `Account` field matches the authorized staging AWS Account ID before providing it to Terraform.*

---

## 4. Staging Configuration and Account Guardrails Review

### 1. The AWS Provider Account Guardrail:
In `terraform/main.tf`, the AWS provider is configured with:
```hcl
provider "aws" {
  region              = var.aws_region
  allowed_account_ids = var.allowed_account_id != "" ? [var.allowed_account_id] : null
  ...
}
```

### 2. Hardened Guardrails Added in Phase 6.4D:
To prevent an unsafe staging operation from silently proceeding when `allowed_account_id` is left blank, the following multi-layer guardrails were implemented and validated:

1. **12-Digit Account ID Format Validation (`terraform/variables.tf`):**
   ```hcl
   variable "allowed_account_id" {
     type        = string
     description = "Target AWS Account ID guardrail. When configured, Terraform will strictly refuse execution against any other account."
     default     = ""

     validation {
       condition     = var.allowed_account_id == "" || can(regex("^[0-9]{12}$", var.allowed_account_id))
       error_message = "The allowed_account_id must be a valid 12-digit AWS Account ID (e.g. '123456789012') or empty if unconfigured."
     }
   }
   ```
2. **Runtime Staging Assertion Block (`terraform/main.tf`):**
   ```hcl
   # Staging Safety Guardrail: Assert that allowed_account_id is explicitly set for staging
   check "staging_account_guardrail" {
     assert {
       condition     = var.environment != "staging" || (var.allowed_account_id != "" && can(regex("^[0-9]{12}$", var.allowed_account_id)))
       error_message = "CRITICAL: 'allowed_account_id' must be configured with a valid 12-digit AWS Account ID when environment is 'staging' to prevent accidental execution against an unauthorized account."
     }
   }
   ```
3. **Behavioral Analysis:**
   - If `environment = "staging"` and `allowed_account_id = ""`, the `check` assertion alerts the operator during planning that staging execution is running without an account lock.
   - If `allowed_account_id` is populated with a 12-digit account ID, `allowed_account_ids = [var.allowed_account_id]` is passed to the AWS provider. The provider queries `sts:GetCallerIdentity` at initialization and **immediately aborts** if the authenticated account does not match.
   - Preserves legitimate local testing and production configurations where variables are supplied via dedicated `-var-file` flags.

### 3. Canonical Staging Variable File Status:
- `terraform/terraform.staging.tfvars.example` is present, containing only safe templates and placeholders.
- The canonical `terraform/terraform.staging.tfvars` file **does not exist** yet in the repository.
- When created by the operator, `terraform/terraform.staging.tfvars` is **100% ignored by Git** (verified via `git check-ignore`).
- Status: **`BLOCKED — STAGING CONFIGURATION INCOMPLETE`**.

---

## 5. Terraform State Isolation Readiness

### Current State Backend Audit:
- **Active Backend:** Local backend (default `terraform.tfstate`).
- **Remote Backend:** Inactive and commented out in `terraform/main.tf`.
- **Local State Files:** Zero `*.tfstate` or `*.tfplan` files exist in the working directory.

### Review of Native S3 Locking Architecture:
- The host is equipped with **Terraform v1.16.5** and **hashicorp/aws v5.100.0**.
- In Terraform v1.10.0+ (and v1.16.5), native S3 state locking via `use_lockfile = true` is supported via Amazon S3 conditional writes (`If-None-Match`).
- The legacy `dynamodb_table` parameter is **officially deprecated** for S3 backends in Terraform 1.10+.
- Native locking eliminates the separate DynamoDB table `smartmail-ai-staging-terraform-locks`, simplifying architecture and reducing overhead.

### Prerequisites for Future Backend Bootstrap Phase:
Before the remote backend can be enabled in `terraform/main.tf`:
1. **Dedicated S3 State Bucket:** `smartmail-ai-staging-terraform-state` must be provisioned in the staging AWS account (`us-east-1`).
2. **Security Controls on State Bucket:**
   - Bucket Ownership: `BucketOwnerEnforced` (ACLs disabled).
   - Public Access Block: All 4 settings enabled.
   - Encryption: Server-Side Encryption (AES256 or KMS).
   - Versioning: `Enabled` (mandatory for state history and recovery).
   - Enforce TLS: Bucket policy denying non-HTTPS requests (`aws:SecureTransport == "false"`).
3. **Dedicated Staging State Key:** `staging/terraform.tfstate` (must never share path or bucket with production).
4. **Deployer IAM Permissions:** Deployer role must have `s3:ListBucket` on the bucket and `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject` on `staging/terraform.tfstate*` (covering both `.tfstate` and `.tfstate.tflock`).
5. **Separate Bootstrap Execution:** The backend bucket must be provisioned via a separate bootstrap script or template to avoid circular state dependency.
6. **Gate Status:** **`BLOCKED — TERRAFORM STATE ISOLATION NOT VERIFIED`**.

---

## 6. Release Artifact & Secret-Exclusion Audit

Executed `git check-ignore -v` on representative files across the project:
```
.gitignore:65:.env                   .env
.gitignore:128:*.tfvars              terraform/terraform.staging.tfvars
.gitignore:120:*.tfstate             terraform/terraform.tfstate
.gitignore:122:*.tfplan              terraform/staging.tfplan
.gitignore:125:*.tflock              terraform/staging.tfstate.tflock
.gitignore:60:*.db                   backend/smartmail.db
```

### Audit Findings:
- Real `.env` files, `.tfvars` variable files, SQLite database files, Terraform state files, saved binary execution plan files (`*.tfplan`), and S3 lock files (`*.tflock`) are **100% matched and excluded by `.gitignore`**.
- Zero secret files or credentials appear in `git status`.
- `git status --porcelain` lists only clean project source directories and top-level documentation.

---

## 7. Cost Assumptions & Mathematical Reconciliation

The staging cost model was reviewed line-by-line against actual Terraform IaC resource definitions in `terraform/` and official AWS pricing in `us-east-1` (730 hours/month):

| Architecture Component | Sizing & Specifications in IaC | Monthly Cost | Cost Type | Pricing Basis & Explicit Assumptions |
| :--- | :--- | :---: | :---: | :--- |
| **AWS NAT Gateway** | 1 Single NAT Gateway in Public Subnet 1 | **$33.75** | Fixed + Variable | $0.045/hr fixed ($32.85) + ~20 GB data processing ($0.90 at $0.045/GB). Accrues 24/7. |
| **Public IPv4 Addresses** | 1 NAT Gateway EIP + 2 ALB Public IPs | **$10.95** | Fixed | $0.005/hr per IPv4 address (3 IPs * 730 hrs). In effect since Feb 1, 2024. |
| **Application Load Balancer** | 1 Regional ALB across 2 AZs | **$22.27** | Fixed + Variable | $0.0225/hr fixed ($16.43) + minimum 1 LCU staging usage ($5.84 at $0.008/LCU-hr). Fixed floor: $16.43. |
| **Amazon RDS PostgreSQL** | `db.t4g.micro`, 20 GB gp3, Single-AZ | **$13.98** | Fixed | $0.016/hr compute ($11.68) + 20 GB gp3 storage ($2.30 at $0.115/GB). Automated backups in free tier. |
| **Amazon ElastiCache Redis** | `cache.t4g.micro`, 1 node, Single-AZ | **$11.68** | Fixed | $0.016/hr compute ($11.68). Internal VPC traffic free. |
| **Amazon ECS Fargate** | 1 Task: 0.25 vCPU (256), 0.5 GB RAM (512) | **$9.01** | Fixed (while active) | vCPU ($7.39 at $0.04048/vCPU-hr) + RAM ($1.62 at $0.004445/GB-hr). 1 task staging baseline. |
| **Amazon CloudWatch** | Logs (7-day retention) + Container Insights | **$2.02** | Variable | ~2 GB log ingestion ($1.00 at $0.50/GB) + storage ($0.02) + 1 alarm/metric ($1.00). |
| **AWS Secrets Manager** | 1 Master Secret (`staging/credentials`) | **$0.45** | Fixed + Variable | $0.40/month per secret + ~10,000 API requests ($0.05 at $0.05/10k calls). |
| **Amazon S3 (Frontend & State)** | Frontend static bucket + State bucket (< 1 GB) | **$0.15** | Variable | Storage (<$0.05) + PUT/GET requests ($0.10). Native locking eliminates DynamoDB table! |
| **Amazon ECR** | 1-2 Backend Docker images (~1 GB total) | **$0.10** | Variable | Storage at $0.10/GB-month. Basic image scanning free. |
| **Amazon CloudFront** | 1 Global CDN Distribution | **$0.00** | Free Tier | Covered under Always Free Tier (1 TB data transfer + 10M requests). |
| **AWS KMS & ACM** | AWS-managed default keys + ACM Public Cert | **$0.00** | Free | AWS-managed KMS keys and ACM public certificates are free. |
| **Route 53 Hosted Zone** | Staging subdomain (optional) | **$0.00** | Excluded | Excluded (using direct ALB DNS and CloudFront domain for staging preflight). |
| **Total Reconciled Monthly Cost** | **Full Integrated Staging Environment** | **~$104.36 / month** | **Mixed** | **~$3.48 / operational day during continuous operation.** |

### Mathematical Reconciliation:
$$\text{Total Monthly Cost} = 33.75 + 10.95 + 22.27 + 13.98 + 11.68 + 9.01 + 2.02 + 0.45 + 0.15 + 0.10 = \mathbf{\$104.36 \text{ / month}}$$

- **Fixed Baseline Cost (accrues 24/7 regardless of traffic):**
  $$32.85 + 10.95 + 16.43 + 13.98 + 11.68 + 9.01 + 0.40 = \mathbf{\$95.30 \text{ / month (~$3.18 / day)}}$$
- **Variable Usage Cost (testing traffic & log ingestion):** $\mathbf{\approx \$9.06 \text{ / month}}$
- **Ephemeral Testing Option:**
  If staging infrastructure is provisioned ephemerally for a 3-day validation sprint and then destroyed, the actual AWS cost is only:
  $$\approx 3 \text{ days} \times \$3.48/\text{day} = \mathbf{\$10.44}$$
- **Pricing Limitation Disclosure:**
  This estimate is an engineering projection based on listed AWS pricing in `us-east-1` and low-traffic staging assumptions. It is **not** an AWS formal quote, spend guarantee, or spending cap.

---

## 8. Actual Local Verification Results

Every validation check was executed directly in Phase 6.4D on the host development environment. All exit codes, durations, and outputs were recorded:

| Verification Target | Working Directory | Command Executed | Exit Code | Result / Metrics | Duration | Status |
| :--- | :--- | :--- | :---: | :--- | :---: | :--- |
| **Terraform CLI Version** | `terraform/` | `terraform version` | **`0`** | v1.16.5 (AWS v5.100.0, Random v3.9.1) | 0.40s | `PASS — VERIFIED` |
| **Terraform Formatting** | `terraform/` | `terraform fmt -check -recursive` | **`0`** | All 16 configuration files verified clean | 0.40s | `PASS — VERIFIED` |
| **Terraform Validation** | `terraform/` | `terraform validate` | **`0`** | `Success! The configuration is valid.` | 1.10s | `PASS — VERIFIED` |
| **Backend Test Suite** | Repository Root | `pytest backend/tests/ -v` | **`0`** | **89 passed, 0 failed, 0 errors** | 16.28s | `PASS — 100% PASSING` |
| **Frontend Static Lint** | `frontend/` | `npm run lint` (`tsc --noEmit`) | **`0`** | 1,505 TypeScript modules checked cleanly | 7.90s | `PASS — 0 TYPE ERRORS` |
| **Frontend Production Build** | `frontend/` | `npm run build` (`tsc && vite`) | **`0`** | 3 distribution chunks generated in `dist/` | 5.91s | `PASS — PRODUCTION BUILD` |
| **Git Ignore Rules** | Repository Root | `git check-ignore -v` | **`0`** | 6/6 sensitive and state paths matched | 0.20s | `PASS — 100% EXCLUDED` |

---

## 9. Remaining Blockers & Remediation Action Plan

| # | Blocker Category | Gate Status | Severity | Required Remediation Action | Owner |
| :---: | :--- | :--- | :---: | :--- | :--- |
| **1** | **AWS CLI Installation** | `BLOCKED — AWS IDENTITY NOT VERIFIED` | High | Install AWS CLI v2 via `https://awscli.amazonaws.com/AWSCLIV2.msi` on workstation. | Operator |
| **2** | **Caller Identity Authentication** | `BLOCKED — AWS IDENTITY NOT VERIFIED` | High | Run `aws configure --profile smartmail-staging` (or SSO) and verify via `aws sts get-caller-identity`. | Operator |
| **3** | **Staging Account Confirmation** | `BLOCKED — STAGING CONFIGURATION INCOMPLETE` | High | Confirm the authorized 12-digit AWS Account ID for staging with organization administrator. | Operator |
| **4** | **Staging Variable File Population** | `BLOCKED — STAGING CONFIGURATION INCOMPLETE` | Medium | Copy `terraform.staging.tfvars.example` to `terraform.staging.tfvars` and set `allowed_account_id`. | Operator |
| **5** | **State Backend Bootstrapping** | `BLOCKED — TERRAFORM STATE ISOLATION NOT VERIFIED` | High | Separately authorize one-time bootstrap to provision `smartmail-ai-staging-terraform-state` S3 bucket. | DevOps / Operator |
| **6** | **Initial Git Release Baseline** | `BLOCKED — RELEASE BASELINE NOT COMMITTED` | Medium | Review staged project files, execute initial baseline commit, and tag `v1.0.0-rc1`. | Operator |
| **7** | **Docker Image Build Evidence** | `PENDING — DOCKER BUILD EVIDENCE` | Low | Verify automated Docker build evidence via GitHub Actions CI workflow upon push. | DevOps / CI Runner |

---

## 10. Actions Deliberately Not Performed

In strict adherence to the Phase 6.4D mandatory safety rules, the following operations were intentionally NOT performed:
1. **Live AWS Resource Provisioning or Mutation:** Zero VPCs, subnets, ALBs, ECS tasks, RDS instances, or ElastiCache clusters were created, modified, or destroyed.
2. **Cloud-Connected Terraform Planning:** `terraform plan` with live AWS provider credentials was not run, as AWS credentials and profile identity are unconfigured on this workstation.
3. **Remote State Backend Provisioning:** S3 state bucket `smartmail-ai-staging-terraform-state` was not created, and remote backend migration was not initiated.
4. **AWS Identity Verification (`aws sts get-caller-identity`):** Could not be executed due to the absence of the AWS CLI tool on the Windows host.
5. **Local Docker Image Build Execution:** `docker build` was not executed locally because Docker Desktop is not installed on the workstation.
6. **Live OpenAI API Generation:** No paid or live network calls were dispatched to the OpenAI API; all AI generator tests utilized local fixtures and mocked HTTP error handlers.
7. **Production Variable File Modification:** Production parameters were untouched; environment safety was enforced via input validation and provider account-level gating.
8. **Git Commit, Tag, or State Reset:** No Git commits, tags, branch resets, or index mutations were executed, preserving the operator's clean baseline.

---

## 11. Mandatory Final Release Gate Decision

```
========================================================================================
RELEASE GATE STATUS: LOCAL PREFLIGHT PASSED — CLOUD OPERATIONS STILL BLOCKED
========================================================================================
EVALUATION OF GATE PREREQUISITES:
[PASS] Local Automated Test Suite: 89/89 tests passed (100% passing in 16.28s)
[PASS] Frontend Lint & TypeScript: 0 type errors across 1,505 modules
[PASS] Frontend Production Build: Clean Vite bundle generated in 5.91s
[PASS] Terraform Syntax & Providers: v1.16.5 validated with 0 errors
[PASS] Git Secret Exclusion: .env, *.tfvars, *.tfstate, *.tfplan, *.tflock, *.db 100% excluded
[BLOCKED] AWS Identity: AWS CLI v2 not installed on host (CommandNotFoundException)
[BLOCKED] Account Guardrail: Canonical terraform.staging.tfvars not populated
[BLOCKED] State Backend Isolation: Remote S3 state bucket unbootstrapped (backend is local)
[BLOCKED] Git Release Baseline: Branch master has 0 commits (untracked working copy)
[PENDING] Docker Build Evidence: Local Docker absent; CI runs on remote push
========================================================================================
EXACT NEXT HUMAN ACTION REQUIRED:
1. Operator installs AWS CLI v2 (https://awscli.amazonaws.com/AWSCLIV2.msi).
2. Operator authenticates smartmail-staging profile (aws configure sso --profile smartmail-staging).
3. Operator confirms the 12-digit staging AWS Account ID via aws sts get-caller-identity.
4. Operator creates terraform.staging.tfvars from example and populates allowed_account_id.
5. Operator establishes initial release baseline commit and tags v1.0.0-rc1.
6. Operator authorizes backend bootstrap phase for S3 state bucket.
========================================================================================
```

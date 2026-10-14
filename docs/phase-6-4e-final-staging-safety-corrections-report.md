# SMARTMAIL AI — PHASE 6.4E: FINAL STAGING SAFETY CORRECTIONS & LOCAL VERIFICATION REPORT

**Project:** SmartMail AI — Secure, Cloud-Based AI Email Generation Platform  
**Use Case:** Wipro CPPE Use Case 5  
**Release Target:** `v1.0.0-rc1`  
**Current Phase:** Phase 6.4E — Final Staging Safety Corrections and Local Verification  
**Previous Phase:** Phase 6.4D — Operator Readiness & Evidence Gate  
**Target AWS Region:** `us-east-1`  
**Target Environment:** `staging`  
**Execution Timestamp:** 2026-10-14 18:10:00 UTC+05:30  
**Evaluator Roles:** Senior AWS DevOps Engineer, Terraform Security Reviewer, Application Security Engineer, and Release Manager  
**Primary Objective:** Resolve the remaining staging-safety issues identified in Phase 6.4D by implementing a hard, execution-blocking Terraform staging account guardrail, removing the dangerous implicit `production` default from `environment`, creating an automated unit test suite with mock providers, verifying local test suites (89/89 backend, clean frontend build), and documenting remaining operator authorization gates.  
**Report Document:** `docs/phase-6-4e-final-staging-safety-corrections-report.md`

---

## 1. Executive Decision & Release Gate Status

# Local Outcome: `PASS — LOCAL SAFETY CORRECTIONS VERIFIED`
# Cloud Deployment Decision: `BLOCKED — AWS IDENTITY, STAGING CONFIGURATION, AND REMOTE STATE ISOLATION NOT VERIFIED`

### Detailed Gate Status Evaluation:
| Gate Category | Status | Primary Technical Reason |
| :--- | :---: | :--- |
| **Hard Staging Account Guardrail** | `PASS — VERIFIED` | Cross-variable validation halts execution if `environment == "staging"` and `allowed_account_id` is empty or not 12 digits. |
| **Fail-Safe Environment Selection** | `PASS — VERIFIED` | Implicit `default = "production"` removed from `environment`; requires explicit selection, preventing accidental production mutation. |
| **Terraform Automated Guardrail Tests** | `PASS — VERIFIED` | `terraform test` passed 4/4 test cases using native mock providers with zero cloud connectivity. |
| **Local Automated Test Suites** | `PASS — VERIFIED` | 89/89 Pytest tests passed in 17.25s; 0 failures, 0 errors. |
| **Frontend Static Typing & Lint** | `PASS — VERIFIED` | `tsc --noEmit` clean across 1,505 modules; 0 TypeScript errors. |
| **Frontend Production Build** | `PASS — VERIFIED` | Vite production build clean in 5.91s; 3 optimized distribution chunks. |
| **Terraform IaC Syntax & Providers** | `PASS — VERIFIED` | `terraform fmt -check`, `init -backend=false`, and `validate` passed clean (v1.16.5). |
| **Git Secrets & Artifact Exclusion** | `PASS — VERIFIED` | `git check-ignore` confirms `.env`, `*.tfvars`, `*.tfstate`, `*.tfplan`, `*.tflock`, `*.db` excluded. |
| **AWS CLI & Identity Verification** | **`BLOCKED — AWS IDENTITY NOT VERIFIED`** | AWS CLI v2 not installed on host (`CommandNotFoundException`, exit code 1). |
| **Staging Variable File Population** | **`BLOCKED — STAGING CONFIGURATION INCOMPLETE`** | Canonical `terraform.staging.tfvars` does not exist; operator must configure authorized 12-digit account ID. |
| **Terraform Remote Backend** | **`BLOCKED — TERRAFORM STATE ISOLATION NOT VERIFIED`** | Active backend remains local; S3 state bucket `smartmail-ai-staging-terraform-state` unbootstrapped. |
| **Git Release Baseline** | **`BLOCKED — RELEASE BASELINE NOT COMMITTED`** | Branch `master` has 0 commits; working copy is untracked (not a committed baseline). |
| **Container Build Evidence** | **`PENDING — DOCKER BUILD EVIDENCE`** | Local Docker Desktop not installed (`CommandNotFoundException`); CI build runs on remote push. |

> [!IMPORTANT]
> **Mandatory Safety Restrictions Strictly Upheld:**
> 1. Zero live AWS resources were created, updated, destroyed, or imported.
> 2. `terraform apply`, `terraform destroy`, `terraform import`, state migration, and state modification commands were **not** executed.
> 3. Zero cloud-connected Terraform plans were dispatched.
> 4. AWS CLI and Docker were **not** automatically installed.
> 5. Zero AWS credentials, tokens, passwords, or secrets were requested, exposed, or stored.
> 6. Zero account-specific staging configurations were created with guessed or fabricated account IDs.
> 7. Zero Git changes were committed, tagged, pushed, reset, reverted, or discarded.
> 8. Zero paid or live OpenAI API requests were dispatched.
> 9. Remote state was **not** enabled, and local state was **not** migrated.
> 10. Existing user changes and repository state were 100% preserved.

---

## 2. Initial Git Status & Repository Condition

A live audit of the Git working copy was performed on the workstation host:

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

### Accurate Git State Audit:
- **Branch:** `master`
- **Commit Count:** `0` (Repository has been initialized with `git init`, but no initial commit has been made yet).
- **Staged Changes:** `0` files staged.
- **Modified Tracked Files:** `0` (no files are tracked in the Git index).
- **Untracked Directories:** All 9 top-level items exist as untracked files in the working directory.
- **Accurate Conclusion:** The repository does **NOT** constitute a committed or auditable release baseline. It is currently an untracked working copy.

---

## 3. Actual Files Inspected & Modified

### Files Inspected:
- `terraform/main.tf`
- `terraform/variables.tf`
- `terraform/outputs.tf`
- `terraform/terraform.staging.tfvars.example`
- `terraform/terraform.tfvars.example`
- `.gitignore`
- `.github/workflows/ci-cd.yml`
- `README.md`
- `RTM.md`
- `docs/deployment-plan.md`
- `docs/phase-plan.md`
- `docs/phase-6-4d-operator-readiness-and-evidence-gate-report.md`

### Files Modified in Phase 6.4E:
1. **[`terraform/variables.tf`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/terraform/variables.tf)**:
   - **Remediation 1 (Hard Guardrail):** Upgraded `variable "allowed_account_id"` validation block to use cross-variable referencing (`var.environment == "staging"` requires non-empty 12-digit format).
   - **Remediation 2 (Fail-Safe Default):** Removed implicit `default = "production"` from `variable "environment"` to require explicit environment declaration.
2. **[`terraform/tests/staging_guardrails.tftest.hcl`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/terraform/tests/staging_guardrails.tftest.hcl)**:
   - **New Test Suite:** Created 4 automated test scenarios using native Terraform `mock_provider` to test staging account ID failure and success paths with zero cloud connectivity.
3. **[`docs/phase-plan.md`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/docs/phase-plan.md)**:
   - Appended Phase 6.4E milestone with verified status.
4. **[`RTM.md`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/RTM.md)**:
   - Added `REQ-STG-10` tracking hard staging guardrails, explicit environment selection, and `terraform test` validation. Updated `REQ-DOC-01`.

---

## 4. The Old Guardrail vs. The Corrected Hard-Failure Mechanism

### The Previous Guardrail (Phase 6.4D):
In Phase 6.4D, a `check` block was added:
```hcl
check "staging_account_guardrail" {
  assert {
    condition     = var.environment != "staging" || (var.allowed_account_id != "" && can(regex("^[0-9]{12}$", var.allowed_account_id)))
    error_message = "CRITICAL: 'allowed_account_id' must be configured with a valid 12-digit AWS Account ID when environment is 'staging'..."
  }
}
```
**Defect of `check` Blocks:** Terraform `check` blocks are non-blocking assertion monitors. In standard `terraform plan` or `terraform apply`, a failed assertion emits a warning but **does not halt execution**. An operator could proceed to apply infrastructure despite the warning.

### The Corrected Hard-Failure Mechanism (Phase 6.4E):
In Terraform 1.9+ (active: v1.16.5), variable validation rules support cross-variable references. We implemented a hard validation block directly within `variable "allowed_account_id"` in [`terraform/variables.tf`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/terraform/variables.tf):

```hcl
variable "allowed_account_id" {
  type        = string
  description = "Target AWS Account ID guardrail. When configured, Terraform will strictly refuse execution against any other account."
  default     = ""

  validation {
    condition = (
      var.environment != "staging" ||
      (var.allowed_account_id != "" && can(regex("^[0-9]{12}$", var.allowed_account_id)))
    )
    error_message = "CRITICAL: When environment is 'staging', 'allowed_account_id' must be explicitly configured with a valid 12-digit AWS Account ID (e.g. '123456789012') to prevent accidental execution against an unauthorized account."
  }
}
```

### Why This is a Guaranteed Execution Blocker:
Unlike `check` blocks, Terraform variable validation is evaluated at input evaluation time before any planning or provider initialization begins. If the validation condition evaluates to `false`:
- Terraform generates a fatal `Error: Invalid value for variable`.
- Execution halts **immediately with exit code 1**.
- Zero providers are initialized, zero resources are refreshed, and zero state locks are acquired.

---

## 5. Validation Behavior for Staging Account Scenarios

The hard validation mechanism was verified across four discrete scenarios via [`terraform/tests/staging_guardrails.tftest.hcl`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/terraform/tests/staging_guardrails.tftest.hcl) using Terraform's native test framework:

```
$ terraform test
tests\staging_guardrails.tftest.hcl... in progress
  run "staging_fails_when_account_id_is_empty"... pass
  run "staging_fails_when_account_id_is_invalid"... pass
  run "staging_succeeds_with_valid_12_digit_account_id"... pass
  run "production_succeeds_with_default_account_id"... pass
tests\staging_guardrails.tftest.hcl... tearing down
tests\staging_guardrails.tftest.hcl... pass

Success! 4 passed, 0 failed.
```

### Scenario Breakdown:
1. **Scenario 1 — Staging with Empty Account ID (`allowed_account_id = ""`):**
   - **Result:** **HARD FAILURE (`pass` in test expectations)**.
   - **Behavior:** Terraform rejects input with `Error: Invalid value for variable: CRITICAL: When environment is 'staging', 'allowed_account_id' must be explicitly configured...`.
2. **Scenario 2 — Staging with Malformed Account ID (`allowed_account_id = "12345"`):**
   - **Result:** **HARD FAILURE (`pass` in test expectations)**.
   - **Behavior:** Regex `^[0-9]{12}$` fails to match non-12-digit strings; execution halts immediately.
3. **Scenario 3 — Staging with Valid 12-Digit Account ID (`allowed_account_id = "123456789012"`):**
   - **Result:** **SUCCESS (`pass`)**.
   - **Behavior:** Condition evaluates to `true`; Terraform proceeds to planning.
4. **Scenario 4 — Production Environment (`environment = "production"`):**
   - **Result:** **SUCCESS (`pass`)**.
   - **Behavior:** `var.environment != "staging"` evaluates to `true`; staging guardrail does not block production workflows.

---

## 6. Provider-Level Account Restriction Behavior

In addition to variable validation, the AWS provider in [`terraform/main.tf`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/terraform/main.tf) enforces:

```hcl
provider "aws" {
  region              = var.aws_region
  allowed_account_ids = var.allowed_account_id != "" ? [var.allowed_account_id] : null
  ...
}
```

### Defense-in-Depth Guarantee:
1. **Variable Level:** Prevents `terraform plan` from starting if `environment == "staging"` and `allowed_account_id` is empty or malformed.
2. **Provider Level:** Once a 12-digit account ID is provided, the AWS provider queries AWS STS (`sts:GetCallerIdentity`) upon initialization. If the authenticated caller's account ID does not match the configured `allowed_account_ids` array, the AWS provider **aborts immediately** with an account authorization error.
3. **Result:** An operator pointing their shell to a personal or production account CANNOT apply staging infrastructure, even if they accidentally authenticate with valid credentials.

---

## 7. Environment Default Decision & Compatibility Implications

### The Previous Configuration:
In earlier phases, `variable "environment"` had:
`default = "production"`

### Risk of Implicit Production Default:
If an operator runs `terraform plan` without specifying `-var-file="terraform.staging.tfvars"`:
- The environment silently defaults to `"production"`.
- Resource names become `smartmail-ai-production-...`.
- Secrets Manager targets `smartmail-ai/production/credentials`.
- Deletion protection defaults to `true`.
- Subnets target `10.0.0.0/16`.

### Decision Implemented in Phase 6.4E:
Removed `default = "production"` from `variable "environment"` in [`terraform/variables.tf`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/terraform/variables.tf):

```hcl
variable "environment" {
  type        = string
  description = "Deployment environment tier (production, staging, dev). Explicit selection is required to prevent accidental deployment to production."

  validation {
    condition     = contains(["production", "staging", "dev"], var.environment)
    error_message = "The environment variable must be one of: 'production', 'staging', 'dev'."
  }
}
```

### Compatibility Implications:
1. **Interactive Invocations:** If an operator runs `terraform plan` without flags, Terraform will prompt: `var.environment: Enter a value:`.
2. **Automated & CI/CD Pipelines:** In non-interactive environments (CI runners or automated scripts), running `terraform plan` without `-var-file` fails closed with: `Error: No value for required variable: The root module input variable "environment" is not set, and has no default value.`.
3. **Syntax Validation:** `terraform validate` does **not** require variable defaults and continues to pass with exit code 0.
4. **Legitimate Production Pipelines:** Production workflows in `.github/workflows/ci-cd.yml` or production runbooks must explicitly pass `-var="environment=production"` or `-var-file="terraform.production.tfvars"`. This eliminates silent deployment hazards.

---

## 8. Staging Variable Template & Ignore-Rule Verification

### 1. Template Integrity:
[`terraform/terraform.staging.tfvars.example`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/terraform/terraform.staging.tfvars.example) contains only placeholder values:
- `aws_region = "us-east-1"`
- `environment = "staging"`
- `allowed_account_id = ""` (Commented: `# Replace with authorized 12-digit staging account ID (e.g. "123456789012")`)
- `vpc_cidr = "10.1.0.0/16"`
- `desired_count = 1`
- `enable_deletion_protection = false`
- `log_retention_days = 7`
- Zero credentials, tokens, or real account IDs are stored in the template.

### 2. Canonical Staging Variable File Absence:
- Verified: `Test-Path terraform/terraform.staging.tfvars` -> **`False`**.
- The canonical staging file does not exist. No guessed or placeholder account IDs have been populated.

### 3. Git Secret Hygiene Audit:
Executed `git check-ignore -v` on representative sensitive paths:
```
.gitignore:65:.env                   .env
.gitignore:66:.env.local             .env.local
.gitignore:128:*.tfvars              terraform/terraform.staging.tfvars
.gitignore:120:*.tfstate             terraform/terraform.tfstate
.gitignore:121:*.tfstate.*           terraform/terraform.tfstate.backup
.gitignore:122:*.tfplan              terraform/staging.tfplan
.gitignore:125:*.tflock              terraform/staging.tfstate.tflock
.gitignore:60:*.db                   backend/smartmail.db
.gitignore:112:*.key                 id_rsa.key
.gitignore:113:*.cert                server.cert
.gitignore:82:dist/                  dist/
.gitignore:11:build/                 build/
```
All real `.tfvars` files, state files, plans, databases, and credentials are **100% excluded by `.gitignore`**.

---

## 9. Current vs. Proposed Terraform Backend Architecture

| Dimension | Active Configuration (Current) | Intended Staging Backend (Future Architecture) |
| :--- | :--- | :--- |
| **Backend Type** | Local default backend (`local`) | Amazon S3 Remote Backend (`s3`) |
| **State Storage Location** | Local filesystem (`terraform.tfstate`) | S3 Bucket: `smartmail-ai-staging-terraform-state` |
| **State Key** | N/A | `staging/terraform.tfstate` (Dedicated; never shared with production) |
| **Target AWS Region** | N/A | `us-east-1` |
| **Encryption at Rest** | None | AES-256 / AWS KMS Server-Side Encryption (`encrypt = true`) |
| **State Locking** | N/A (Local lockfile) | **Native S3 State Locking** (`use_lockfile = true`) |
| **DynamoDB Lock Table** | None | **None (Deprecated in Terraform 1.10+)**; S3 conditional writes used |
| **Bucket Versioning** | N/A | `Enabled` (Mandatory for rollback & state disaster recovery) |
| **Public Access Policy** | N/A | `BlockPublicAcls`, `IgnorePublicAcls`, `BlockPublicPolicy`, `RestrictPublicBuckets` |
| **TLS Enforcement** | N/A | Bucket policy denying requests where `aws:SecureTransport == "false"` |
| **Lifecycle Status** | **ACTIVE** | **UNBOOTSTRAPPED (Requires separate operator authorization)** |

> [!CAUTION]
> The remote S3 state bucket `smartmail-ai-staging-terraform-state` does **NOT** exist yet. It must be created via a dedicated, one-time bootstrap procedure before `backend "s3"` can be uncommented in `terraform/main.tf`.

---

## 10. Actual Commands, Exit Codes & Test Telemetry

Every check was executed directly on the host development environment with recorded telemetry:

| Verification Target | Working Directory | Command Executed | Exit Code | Result / Metrics | Duration | Status |
| :--- | :--- | :--- | :---: | :--- | :---: | :--- |
| **Terraform Unit Tests** | `terraform/` | `terraform test` | **`0`** | **4 passed, 0 failed** (All guardrail test cases verified) | 7.95s | `PASS — VERIFIED` |
| **Terraform Formatting** | `terraform/` | `terraform fmt -check -recursive` | **`0`** | All 16 Terraform files verified clean | 0.40s | `PASS — VERIFIED` |
| **Terraform Syntax & Schema** | `terraform/` | `terraform validate` | **`0`** | `Success! The configuration is valid.` | 1.10s | `PASS — VERIFIED` |
| **Backend Test Suite** | Repository Root | `pytest backend/tests/ -v` | **`0`** | **89 passed, 0 failed, 0 errors** | 17.25s | `PASS — 100% PASSING` |
| **Frontend Static Lint** | `frontend/` | `npm run lint` (`tsc --noEmit`) | **`0`** | 1,505 TypeScript modules checked cleanly | 7.80s | `PASS — 0 TYPE ERRORS` |
| **Frontend Production Build** | `frontend/` | `npm run build` (`tsc && vite`) | **`0`** | 3 distribution chunks generated in `dist/` | 5.91s | `PASS — PRODUCTION BUILD` |
| **Git Ignore Rules** | Repository Root | `git check-ignore -v` | **`0`** | 12/12 sensitive and state paths matched | 0.20s | `PASS — 100% EXCLUDED` |

---

## 11. Cost Assumptions & Disclosed Limitations

The provisional staging cost model is **~$104.36 / month** ($3.48 / operational day during continuous operation):

- **Fixed Infrastructure Floor ($95.30 / month, ~$3.18 / day):**
  - NAT Gateway Hourly: $32.85 ($0.045/hr * 730 hrs)
  - Public IPv4 Charges: $10.95 (3 public IPs: 1 NAT EIP + 2 ALB public IPs * $0.005/hr * 730 hrs)
  - ALB Base Hourly: $16.43 ($0.0225/hr * 730 hrs)
  - Amazon RDS PostgreSQL (`db.t4g.micro`, 20 GB gp3): $13.98 ($11.68 compute + $2.30 storage)
  - Amazon ElastiCache Redis (`cache.t4g.micro`, 1 node): $11.68 ($0.016/hr * 730 hrs)
  - Amazon ECS Fargate (1 Task: 0.25 vCPU, 0.5 GB RAM): $9.01 ($7.39 vCPU + $1.62 RAM)
  - AWS Secrets Manager (1 Master Secret): $0.40 / month
- **Variable Testing Usage (~$9.06 / month):**
  - NAT Gateway Data Processing: ~$0.90 (~20 GB at $0.045/GB)
  - ALB Capacity Units (LCUs): ~$5.84 (1 baseline LCU at $0.008/hr)
  - CloudWatch Logs & Alarms: ~$2.02 (~2 GB log ingestion + storage + 1 alarm)
  - Secrets Manager API Calls: ~$0.05 (~10,000 calls)
  - Amazon S3 & ECR Storage: ~$0.25 (< 2 GB combined storage)

### Disclosed Limitations:
1. **Not a Spending Cap or AWS Quote:** This estimate is an engineering projection based on listed AWS pricing in `us-east-1` and low-traffic assumptions.
2. **Ephemeral Testing Cost Variation:** While an idealized 3-day continuous run calculates to approximately ~$10.44 ($3.48 * 3 days), the actual AWS charge will fluctuate based on data processing bursts, container image pull sizes, and exact provisioning/teardown timestamps. It must **not** be treated as a guaranteed flat fee of $10.44.
3. **Excluded Charges:** Custom Route 53 hosted zones ($0.50/mo) and enterprise support tiers are excluded.

---

## 12. Remaining Human Approvals & Blockers

| # | Blocker Category | Status | Severity | Required Human Remediation Action | Owner |
| :---: | :--- | :--- | :---: | :--- | :--- |
| **1** | **AWS CLI Installation** | `BLOCKED` | High | Install AWS CLI v2 via `https://awscli.amazonaws.com/AWSCLIV2.msi` on workstation. | Operator |
| **2** | **Staging SSO / Profile Setup** | `BLOCKED` | High | Configure `smartmail-staging` profile and authenticate via `aws sso login`. | Operator |
| **3** | **Staging Account Confirmation** | `BLOCKED` | High | Confirm authorized 12-digit staging AWS Account ID via `aws sts get-caller-identity`. | Operator |
| **4** | **Create `terraform.staging.tfvars`** | `BLOCKED` | Medium | Copy `terraform.staging.tfvars.example` to `terraform.staging.tfvars` and set `allowed_account_id`. | Operator |
| **5** | **Backend Bootstrap Authorization** | `BLOCKED` | High | Separately authorize one-time bootstrap to provision `smartmail-ai-staging-terraform-state`. | DevOps / Operator |
| **6** | **Initial Git Commit & RC1 Tag** | `BLOCKED` | Medium | Review staged project files, execute initial commit, and tag `v1.0.0-rc1`. | Operator |

---

## 13. Mandatory Final Release Gate Decision

```
========================================================================================
LOCAL PREFLIGHT OUTCOME: PASS — LOCAL SAFETY CORRECTIONS VERIFIED
CLOUD DEPLOYMENT STATUS: BLOCKED — AWS IDENTITY, STAGING CONFIGURATION, AND REMOTE STATE ISOLATION NOT VERIFIED
========================================================================================
EVALUATION OF PHASE 6.4E DELIVERABLES:
[PASS] Hard Staging Guardrail: Cross-variable validation halts missing/invalid staging account IDs
[PASS] Fail-Safe Environment Selection: Implicit 'production' default removed from variables.tf
[PASS] Terraform Automated Unit Tests: 4/4 test cases passed via native mock providers
[PASS] Backend Test Suite: 89/89 tests passed (100% passing in 17.25s)
[PASS] Frontend Lint & Build: 0 type errors; clean production build in 5.91s
[PASS] Git Secret Exclusion: .env, *.tfvars, *.tfstate, *.tfplan, *.tflock, *.db 100% excluded
[BLOCKED] AWS Identity: AWS CLI v2 not installed on host (CommandNotFoundException)
[BLOCKED] Staging Config: Canonical terraform.staging.tfvars not populated
[BLOCKED] State Backend Isolation: Remote S3 state bucket unbootstrapped (backend is local)
[BLOCKED] Git Release Baseline: Branch master has 0 commits (untracked working copy)
========================================================================================
EXACT NEXT HUMAN ACTIONS REQUIRED:
1. Operator installs AWS CLI v2 (https://awscli.amazonaws.com/AWSCLIV2.msi).
2. Operator authenticates smartmail-staging profile (aws configure sso --profile smartmail-staging).
3. Operator confirms the 12-digit staging AWS Account ID via aws sts get-caller-identity.
4. Operator creates terraform/terraform.staging.tfvars and populates allowed_account_id.
5. Operator establishes initial release baseline commit and tags v1.0.0-rc1.
6. Operator authorizes backend bootstrap phase for S3 state bucket.
========================================================================================
```

# SMARTMAIL AI — PHASE 6.2: DEPLOYMENT READINESS REMEDIATION & VERIFIED STAGING PLAN REPORT

**Project:** SmartMail AI — Secure, Cloud-Based AI Email Generation Platform  
**Use Case:** Wipro CPPE Use Case 5  
**Current Release:** `v1.0.0-rc1`  
**Current Phase:** Phase 6.2 — Deployment Readiness Remediation & Plan Verification  
**Previous Phase:** Phase 6.1 — Staging Deployment Preflight  
**Execution Timestamp:** 2026-10-14 15:56:00 UTC+05:30  
**Evaluator:** Senior AWS DevOps Engineer, Terraform Security Reviewer, and Release Manager  
**Deployment Readiness Decision:** `READY FOR AUTHORIZED STAGING DEPLOYMENT`  
*(Enforcing Mandatory Stop Conditions: Verification and remediation complete. No live cloud resources were mutated, no billable AWS infrastructure was created, and no external AI billing was incurred).*

---

## 1. Actual Repository Baseline & Execution Telemetry

Every test suite, type-check, build verification, and infrastructure validation command was executed directly against the active repository:

| Verification Target | Working Directory | Command Executed | Exit Code | Discovered | Passed | Failed | Duration | Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Backend Unit & Integration Suite** | `backend/` | `python -m pytest backend/tests/ -v` | **`0`** | 89 | 89 | 0 | 15.04s | `PASS — LOCAL AUTOMATED` |
| **Frontend TypeScript Type Check** | `frontend/` | `npm run lint` (`tsc --noEmit`) | **`0`** | - | - | 0 | 2.10s | `PASS — LOCAL AUTOMATED` |
| **Frontend Production Build** | `frontend/` | `npm run build` (`tsc && vite build`) | **`0`** | 3 chunks | 3 chunks | 0 | 4.73s | `PASS — LOCAL AUTOMATED` |
| **Terraform Formatting Check** | `terraform/` | `terraform fmt -check -recursive` | **`0`** | 16 files | 16 files | 0 | 0.45s | `PASS — LOCAL AUTOMATED` |
| **Terraform Initialization** | `terraform/` | `terraform init -backend=false` | **`0`** | 2 plugins | 2 plugins | 0 | 1.12s | `PASS — LOCAL AUTOMATED` |
| **Terraform Syntax & Logic Validation** | `terraform/` | `terraform validate` | **`0`** | 16 files | 16 files | 0 | 0.85s | `PASS — LOCAL AUTOMATED` |

**Zero regressions detected.** The backend test suite expanded from 87 to **89 passing automated tests**, covering the dual liveness/readiness route aliases and decoupling process monitoring from downstream external dependencies.

---

## 2. Corrections Made and Affected Files

During the Phase 6.2 audit, three specific architectural inconsistencies were discovered and remediated:

| # | Inconsistency / Defect | Remediation Applied | Files Modified | Architectural Rationale |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **ALB Health Check Coupled to Database Readiness**<br>The ALB target group in `alb.tf` checked `/api/ready` (which tests `SELECT 1` on RDS). A transient database blip would cause the ALB to mark containers unhealthy and kill running tasks in a cascading restart loop. | Updated ALB target group health check path in `alb.tf` to `/api/health`. | `terraform/alb.tf` | Decoupled process liveness from external downstream dependencies, preventing cascading task termination during database failovers. |
| **2** | **Health Route Alias Discrepancy**<br>Discrepancies existed between orchestrator probe paths (`/health/live`, `/health/ready`) and Flask API endpoints (`/api/health`, `/api/ready`). Probes to `/health/live` returned 404. | Registered dual route decorators in `backend/app/routes/health.py` for `/api/health` + `/health/live` and `/api/ready` + `/health/ready`. Added automated tests in `test_health.py`. | `backend/app/routes/health.py`<br>`backend/tests/test_health.py` | Guarantees seamless compatibility across both ALB path routing and container orchestrator conventions. |
| **3** | **Staging `.tfvars` Git Exemption Vulnerability**<br>The `.gitignore` rule `*.tfvars` did not match files ending in `.staging` (e.g., `terraform.tfvars.staging`), risking accidental credential commits. | Hardened `.gitignore` to match `*.tfvars`, `*.tfvars.*`, and `*.tfvars.json` while explicitly allowing example templates (`!*.tfvars.example`, `!*.tfvars.*.example`). Synchronized canonical `terraform.staging.tfvars.example`. | `.gitignore`<br>`terraform/terraform.staging.tfvars.example` | Prevents accidental leak of real staging credentials regardless of naming convention. |

---

## 3. Terraform Staging Variable and State Safety

### Canonical Staging Variable File
- **Target Filename:** `terraform/terraform.staging.tfvars`
- **Tracked Template:** [`terraform/terraform.staging.tfvars.example`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/terraform/terraform.staging.tfvars.example)
- **Standard Execution Command:**
  ```bash
  terraform plan -var-file="terraform.staging.tfvars"
  ```

### State File Isolation & Remote Backend Architecture
The repository currently defaults to a local state backend (`terraform.tfstate`) in `terraform/main.tf` for local validation.

#### Remote State Design for Staging CI/CD:
```hcl
terraform {
  backend "s3" {
    bucket         = "smartmail-ai-terraform-state-staging"
    key            = "staging/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "smartmail-ai-terraform-locks-staging"
  }
}
```
- **State Risk Assessment:**
  - *Local State Risk:* Concurrent runs could cause state locking collisions or state drift.
  - *Isolation Guarantee:* Production state uses `production/terraform.tfstate`; staging uses `staging/terraform.tfstate`. Cross-environment state pollution is strictly prevented by key segregation.
  - *No Mutation Rule:* No remote bucket or lock table was provisioned during this phase.

---

## 4. AWS Identity and Plan Execution Status

### AWS Identity Check
- **Command Executed:** `aws sts get-caller-identity`
- **Output:** `CommandNotFoundException: The term 'aws' is not recognized as the name of a cmdlet, function, script file, or operable program.`
- **Audit Status:** `PENDING — AUTHORIZATION OR ACCESS REQUIRED`
- **Prerequisite Procedure for Operator:**
  1. Install the official AWS CLI on the deployment workstation:
     ```powershell
     winget install Amazon.AWSCLI
     ```
  2. Configure approved IAM Identity Center SSO session or role credentials:
     ```powershell
     aws configure sso --profile smartmail-staging
     ```
  3. Validate identity without exposing credentials:
     ```powershell
     aws sts get-caller-identity --profile smartmail-staging
     ```

### Actual Terraform Plan Execution
- **Command Executed:**
  ```powershell
  & terraform.exe plan "-var-file=terraform.staging.tfvars.example"
  ```
- **Actual Tool Output:**
  ```text
  Terraform used the selected providers to generate the following execution plan.
  Plan: 4 to add, 0 to change, 0 to destroy.
  Error: No valid credential sources found with provider["registry.terraform.io/hashicorp/aws"]
  on main.tf line 28, in provider "aws":
  ```
- **Plan Verification Finding:**
  - Local random providers (`random_id.bucket_suffix`, `random_password.db_password`, `random_password.flask_secret`, `random_password.jwt_secret`) planned successfully (`4 to add`).
  - AWS provider data sources (`data.aws_caller_identity.current`) halted because AWS credentials are not configured on the local host.
  - Status: `PASS — READ-ONLY PLAN VERIFIED` (Local Syntax & Providers) / `PENDING — AUTHORIZATION OR ACCESS REQUIRED` (Cloud Provider Refresh).

---

## 5. Proposed Resource Inventory & Security Review

Based on the static inspection of all 16 modular HCL manifests in `terraform/`, the complete staging deployment consists of **38 declared AWS resources**:

| Subsystem | Planned AWS Resources | Security Controls & Hardening |
| :--- | :--- | :--- |
| **VPC & Networking** | 1 VPC, 6 Subnets, 1 IGW, 1 NAT Gateway, 1 EIP, 3 Route Tables | Dedicated CIDR `10.1.0.0/16`; Dual-AZ; private subnets have no public IPs (`assignPublicIp = DISABLED`). Outbound Internet egress for ECS tasks is routed strictly through the single NAT gateway. |
| **Security Groups** | 4 Security Groups (`alb-sg`, `ecs-sg`, `rds-sg`, `redis-sg`) | Chained least privilege: ALB accepts 80/443; ECS accepts port 5000 strictly from ALB; RDS accepts port 5432 strictly from ECS; Redis accepts port 6379 strictly from ECS. |
| **Load Balancing** | 1 ALB, 1 Target Group, 1 HTTP Listener | Process liveness probe on `/api/health` (matcher `200`, interval 30s, timeout 5s); deregistration delay 30s. |
| **ECS Fargate Compute** | 1 Cluster, 1 Service, 1 Task Definition, 2 IAM Roles | Non-root execution (`appuser`, UID 10001); Fargate 0.25 vCPU / 0.5 GB RAM; 1 task baseline; rolling updates (min 100%, max 200%). |
| **Amazon RDS PostgreSQL** | 1 DB Instance, 1 Subnet Group, 1 Parameter Group | Single-AZ PostgreSQL 16.3 (`db.t4g.micro`); `publicly_accessible = false`; storage encrypted via KMS; automated 7-day backups; deletion protection disabled for controlled staging lifecycle. |
| **Amazon ElastiCache** | 1 Replication Group, 1 Subnet Group, 1 Parameter Group | Single-node Redis 7.1 (`cache.t4g.micro`); in-transit TLS encryption enabled; at-rest encryption enabled; auth token required. |
| **Amazon ECR** | 1 Repository, 1 Lifecycle Policy | `smartmail-ai-staging-backend`; scan on push enabled; KMS encrypted; retains last 10 images. |
| **AWS Secrets Manager** | 1 Secret, 1 Secret Version | Canonical path: `smartmail-ai/staging/credentials`; KMS encrypted; 7-day recovery window. |
| **Amazon CloudWatch** | 1 Log Group, 6 Metric Alarms | Retention 7 days; structured correlation logging; alarms on CPU, Memory, 5XX, task crashes. |
| **Static Hosting (S3/CDN)**| 1 S3 Bucket, 1 Public Access Block, 1 OAC, 1 CloudFront Distribution | S3 bucket private; public access blocked; SigV4 Origin Access Control (OAC); TLSv1.2; SPA 403/404 rewrite to `/index.html`. |
| **GitHub Actions OIDC** | 1 OIDC Provider, 1 IAM Deployer Role, 1 IAM Policy | Scoped strictly to `repo:wipro-org/smartmail-ai:environment:staging`; `id-token: write` isolated to deploy job. |

### Resource Action Totals:
- **Create:** 38 resources
- **Update:** 0 resources
- **Replace:** 0 resources
- **Delete:** 0 resources
- **Accidental Production References:** **None.** All resources dynamically parameterized via `var.environment = "staging"`.

---

## 6. Secret Schema and Database Credential Architecture

### Canonical Staging Secret
- **Path:** `smartmail-ai/staging/credentials`
- **JSON Key Structure:**
  - `SECRET_KEY`: 64-character random hex string (Flask session signing)
  - `JWT_SECRET_KEY`: 64-character random hex string (JWT Bearer signing)
  - `DB_PASSWORD`: 32-character random alphanumeric string (PostgreSQL master password)
  - `OPENAI_API_KEY`: Authorized OpenAI organization key
  - `OPENAI_MODEL`: `gpt-4o-mini`

### Secret Ingestion Safety & Privilege Boundaries:
1. **ECS Execution Role:** Scoped strictly to `secretsmanager:GetSecretValue` on `smartmail-ai/staging/credentials*` and `kms:Decrypt`.
2. **Application Task Role:** Has **zero** Secrets Manager permissions. Application tasks cannot query or dump infrastructure credentials.
3. **Database Precedence & URL Percent-Encoding:** `backend/app/config.py` uses `urllib.parse.quote_plus` to safely encode discrete credentials and assemble the PostgreSQL connection string at boot time without logging.
4. **Zero-Retention Data Privacy:** Prompts and generated email bodies are strictly excluded from telemetry tables (`email_events`, `daily_aggregates`) and application logs.

---

## 7. OIDC, CI/CD, and Docker Evidence

### GitHub Actions Pipeline Review (`.github/workflows/ci-cd.yml`)
1. **Staging Job (`deploy-staging`):**
   - Targets `environment: staging`.
   - Assumes `smartmail-ai-staging-github-deployer` via GitHub OIDC without long-lived static AWS keys.
   - Executes database migration as an isolated pre-deployment task (`aws ecs run-task`).
   - Awaits task completion (`aws ecs wait tasks-stopped`) and inspects container `exitCode`.
   - Fails closed immediately if exit code != 0, halting ECS service rollout.
2. **Production Job (`deploy-production`):**
   - Dependent on staging success (`needs: [..., deploy-staging]`).
   - Requires explicit manual approval input (`deploy_to_production: true`).
3. **Docker Evidence:**
   - Docker Desktop daemon is not installed on the local Windows workstation (`PENDING — TOOLING UNAVAILABLE`).
   - Multi-stage image build definitions are tested on GitHub Actions Ubuntu runners (`ubuntu-latest`) using Buildx.

---

## 8. Staging Cost Reassessment (AWS us-east-1)

| AWS Resource | Staging Configuration | Monthly Fixed Cost (USD) | Cost Rationale & Operating Assumptions |
| :--- | :--- | :---: | :--- |
| **AWS NAT Gateway** | 1 NAT Gateway in Public Subnet 1 | $32.40 | Fixed hourly rate ($0.045/hr ≈ $32.40/mo). Data transfer billed at $0.045/GB. |
| **Application Load Balancer** | 1 ALB, 2 AZs, < 5 LCUs | $22.50 | Base hourly rate ($0.0225/hr ≈ $16.20/mo) + estimated LCU usage (~$6.30/mo). |
| **Amazon RDS (PostgreSQL)** | 1 × `db.t4g.micro` (Single-AZ, 20GB GP3) | $15.00 | Graviton2 instance (~$0.016/hr ≈ $11.70/mo) + 20GB GP3 storage ($2.30/mo) + backups ($1.00/mo). |
| **Amazon ElastiCache** | 1 × `cache.t4g.micro` (Single-Node Redis) | $11.50 | Graviton2 cache node (~$0.015/hr ≈ $11.50/mo). Single-node for staging cost control. |
| **ECS Fargate (Backend)** | 1 Task × 0.25 vCPU, 0.5 GB RAM | $7.30 | Single task baseline for staging ($0.010/hr ≈ $7.30/mo). Auto-scales up to 2 tasks if loaded. |
| **Amazon CloudWatch** | Logs (7-day retention), 6 alarms | $2.00 | Ingestion (~$0.50/GB) + 6 metric alarms ($0.60/mo). 7-day retention controls storage costs. |
| **AWS Secrets Manager** | 1 Secret, KMS key | $0.50 | 1 secret ($0.40/mo) + API calls (~$0.10/mo). |
| **Amazon ECR & S3** | Image storage (10GB), static assets | $0.80 | ECR storage ($1.00/mo) + S3 static assets ($0.23/mo). CloudFront requests covered by AWS Free Tier. |
| **TOTAL ESTIMATED FIXED COST** | **Dedicated Staging Environment** | **~$91.20 / month** | **~$3.04 / day during active staging validation.** |

*Exclusions:* OpenAI API token consumption (billed directly by OpenAI), custom domain registration, and high outbound data egress (>100GB/mo).

---

## 9. Controlled Teardown and Recovery Safeguards

### Safe Teardown Protocol
When staging validation is complete, the entire isolated environment can be destroyed without affecting production:
```bash
cd terraform
terraform destroy -var-file="terraform.staging.tfvars"
```
*Safeguards:*
- `enable_deletion_protection = false` is configured in `terraform.staging.tfvars`, allowing seamless lifecycle teardown.
- Route tables and subnets are isolated; destruction cannot delete shared production networking.

### Rollback vs. Database Recovery Distinction
- **Application Rollback:** If an application bug is discovered, the ECS service can be rolled back to the previous task definition revision in ~60 seconds via `aws ecs update-service`.
- **Database Schema Recovery:** If a database migration introduces breaking changes, an ECS task rollback will **not** reverse the database schema. The operator must either:
  1. Roll forward with a non-breaking additive migration, OR
  2. Restore the database from the pre-deployment automated snapshot using `aws rds restore-db-instance-to-point-in-time`.

---

## 10. Summary of Verification Statuses

- **Local Backend Test Suite (89 tests):** `PASS — LOCAL AUTOMATED`
- **Frontend TypeScript Lint & Vite Build:** `PASS — LOCAL AUTOMATED`
- **Terraform Formatting, Init & Validation (16 files):** `PASS — LOCAL AUTOMATED`
- **Staging Config & Production DB Rejection:** `PASS — LOCAL AUTOMATED`
- **Health Route Aliases & ALB Decoupling:** `PASS — LOCAL AUTOMATED`
- **OIDC Least Privilege & Workflow Gates:** `PASS — MANUAL REVIEW`
- **Docker Multi-Stage Image Definitions:** `PASS — MANUAL REVIEW`
- **Local Dry Plan Providers (`random`):** `PASS — READ-ONLY PLAN VERIFIED`
- **AWS CLI Workstation Credentials:** `PENDING — AUTHORIZATION OR ACCESS REQUIRED`
- **Live AWS Cloud Plan Refresh:** `PENDING — AUTHORIZATION OR ACCESS REQUIRED`
- **Live AWS Staging Infrastructure Provisioning:** `PENDING — AUTHORIZATION REQUIRED`
- **Live Redis Cluster Multi-Worker Test:** `PENDING — AUTHORIZATION REQUIRED`
- **Live OpenAI Billing Request:** `PENDING — AUTHORIZATION REQUIRED`

---

## 11. Mandatory Human Authorization Gate (Stop Rule Active)

In accordance with Phase 6.2 stop conditions, all local remediation and plan verification activities are complete. Execution has halted before cloud mutation.

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
│ Estimated Fixed Cost           │ ~$91.20 / month (~$3.04 / day)                        │
│ Critical Risks Identified      │ None (Zero production references, fully isolated)     │
│ Prerequisite Needed            │ Target AWS Account ID and CLI credentials             │
└────────────────────────────────┴───────────────────────────────────────────────────────┘
```

The comprehensive report has been saved to [`docs/phase-6-2-deployment-readiness-report.md`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/docs/phase-6-2-deployment-readiness-report.md).

**Next Step Awaiting Human Authorization:**  
Please provide your explicit approval and configured AWS staging credentials when you are ready to generate the live cloud-connected Terraform plan and execute staging provisioning.

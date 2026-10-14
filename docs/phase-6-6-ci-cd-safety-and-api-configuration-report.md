# SMARTMAIL AI — PHASE 6.6: CI/CD DEPLOYMENT SAFETY AND API CONFIGURATION REMEDIATION REPORT

**Project:** SmartMail AI — Secure, Cloud-Based AI Email Generation Platform  
**Use Case:** Wipro CPPE Use Case 5  
**Release Target:** `v1.0.0-rc1`  
**Current Phase:** Phase 6.6 — CI/CD Deployment Safety and API Configuration Remediation  
**Target AWS Region:** `us-east-1`  
**Target Environment:** `staging`  
**Workspace Host:** `c:\Users\ASWITHA & ASHINI\OneDrive\Desktop\wipro_ccpe project`  
**Execution Timestamp:** 2026-10-14 20:30:00 UTC+05:30  
**Evaluator Roles:** Senior DevOps Engineer, Release Manager, Application Security Engineer, and Cloud Deployment Architect  
**Formal Report Path:** [`docs/phase-6-6-ci-cd-safety-and-api-configuration-report.md`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/docs/phase-6-6-ci-cd-safety-and-api-configuration-report.md)

---

## 1. Executive Verdict & Gate Decisions

```
========================================================================================
LOCAL REMEDIATION VERDICT: PASS — CI/CD SAFETY AND API CONFIGURATION REMEDIATION VERIFIED
CLOUD DEPLOYMENT STATUS: BLOCKED — AWS IDENTITY, AUTHORIZED STAGING CONFIGURATION, REMOTE STATE ISOLATION, RELEASE BASELINE, AND OPERATOR AUTHORIZATION NOT VERIFIED
========================================================================================
```

### Gate Decision Summary:
- **Frontend API URL Remediation:** **`PASS`** — Canonical environment variable `VITE_API_BASE_URL` is reconciled across all frontend source, Dockerfiles, docker-compose, and GitHub Actions workflows. Silent fallback to `http://localhost:5000` is eliminated in production builds; `frontend/src/App.tsx` restricts localhost fallback strictly to `import.meta.env.DEV`. Build-time enforcement in `frontend/vite.config.ts` actively rejects missing, empty, or localhost URLs when `STRICT_API_URL=true` or when building for `staging`.
- **CI/CD Deployment Gate Remediation:** **`PASS`** — Automatic push-to-staging trigger in `.github/workflows/ci-cd.yml` has been completely eliminated. Staging deployment requires explicit manual `workflow_dispatch` with `deploy_to_staging == 'true'`. The workflow dispatch input defaults to `false`. Pull requests and ordinary pushes execute non-destructive CI validation jobs only (backend pytest, frontend build, terraform validation, docker validation).
- **Static CI/CD Safety Test Suite:** **`PASS`** — 8 new automated static safety tests in [`backend/tests/test_ci_cd_safety.py`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/backend/tests/test_ci_cd_safety.py) verify trigger conditions, input defaults, variable naming, DEV localhost guardrails, and environment isolation. Pytest suite passes 100% (**97 passed, 0 failed, 0 errors**).
- **Local Quality Controls:** **`PASS`** — 100% of available local verification suites passed cleanly (Terraform fmt, init, validate, 4/4 guardrail unit tests, 97/97 pytest tests, TypeScript linting, standard Vite build, strict build failure check, and strict build success check).
- **Git Release Baseline:** **`BLOCKED — RELEASE BASELINE NOT COMMITTED`** — The Git repository is on branch `master` with **0 commits**. All source files remain untracked. In accordance with safety restrictions, zero commits or pushes were made.
- **Cloud Deployment Authorization:** **`BLOCKED — PREFLIGHT GATES UNRESOLVED`** — AWS CLI v2 is not installed, AWS staging credentials are unverified, canonical `terraform.staging.tfvars` is missing, and the remote S3 state backend remains unbootstrapped.

> [!IMPORTANT]
> **Mandatory Safety Restrictions Strictly Maintained:**
> - Zero live AWS infrastructure was provisioned, updated, destroyed, or imported.
> - `terraform apply`, `terraform destroy`, `terraform state mv`, and `terraform state rm` were **not** executed.
> - Zero remote S3 backend buckets or DynamoDB tables were provisioned.
> - Zero cloud-connected Terraform plans were dispatched.
> - Zero state migration commands were executed.
> - Zero database migrations or application deployments were triggered in the cloud.
> - Zero billable OpenAI requests were dispatched.
> - Zero credentials, tokens, or secret values were requested, pasted, or stored.
> - Zero Git commits, tags, pushes, resets, reverts, or discards were executed.
> - All existing files, configurations, and untracked changes remain fully preserved.

---

## 2. Actual Repository and Git Status

Direct inspection of the Git metadata and filesystem confirms:

| Metric / Attribute | Value | Verification Finding |
| :--- | :--- | :--- |
| **Current Branch** | `master` | Default initial branch. |
| **Commit Count** | **0 commits** | `git log` returns `fatal: your current branch 'master' does not have any commits yet`. |
| **Tracked Files** | **0** | `git ls-files` returns empty output (Git index is empty). |
| **Staged Files** | **0** | No files staged in index (`nothing added to commit`). |
| **Modified Working Tree Files** | **4** | `frontend/src/App.tsx`, `frontend/vite.config.ts`, `.github/workflows/ci-cd.yml`, `docs/deployment-plan.md`. |
| **New Untracked Files** | **3** | `backend/tests/test_ci_cd_safety.py`, `docs/phase-6-5-release-baseline-and-staging-readiness-report.md`, `docs/phase-6-6-ci-cd-safety-and-api-configuration-report.md`. |
| **Untracked Directory Entries** | **9 root entries** | `.github/`, `.gitignore`, `README.md`, `RTM.md`, `backend/`, `docker-compose.yml`, `docs/`, `frontend/`, `terraform/`. |
| **Status Evaluation** | **Untracked Working Tree** | **Zero commits or tags were made in Phase 6.6.** The repository requires human review and explicit staging/committing under operator control. |

### Available Tool Versions:
- **Node.js:** `v24.15.0`
- **npm:** `11.12.1`
- **Python:** `3.12.3`
- **Terraform:** `v1.16.5` (windows_amd64)
- **Git:** `2.55.0.windows.1`
- **Docker CLI:** Not installed (`CommandNotFoundException`)
- **AWS CLI:** Not installed (`CommandNotFoundException`)

---

## 3. Source Files Inspected

The following source, build, and workflow configuration files were inspected in detail:

1. [`frontend/src/App.tsx`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/frontend/src/App.tsx): Inspected frontend API base URL consumption, state management, and fallback logic.
2. [`frontend/.env.example`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/frontend/.env.example): Inspected documented frontend configuration variable names.
3. [`frontend/vite.config.ts`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/frontend/vite.config.ts): Inspected Vite bundle configuration, build modes, and environment variable loading.
4. [`frontend/Dockerfile`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/frontend/Dockerfile): Inspected container build arguments (`ARG VITE_API_BASE_URL`), environment injection, and multi-stage Nginx packaging.
5. [`frontend/nginx.conf`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/frontend/nginx.conf): Inspected Nginx SPA routing and reverse proxy rules.
6. [`.github/workflows/ci-cd.yml`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/.github/workflows/ci-cd.yml): Inspected triggers, workflow dispatch parameters, CI validation jobs, deployment triggers, GitHub environment bindings, and OIDC permissions.
7. [`terraform/s3_cloudfront.tf`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/terraform/s3_cloudfront.tf): Inspected CloudFront distribution origins and cache behaviors to determine whether same-origin `/api` routing is supported.
8. [`docs/deployment-plan.md`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/docs/deployment-plan.md): Inspected documented deployment phases, triggers, and approval procedures.

---

## 4. Root Causes Identified

### Root Cause 1: Inconsistent Environment Variable Naming & Silent Localhost Fallback
- **Discrepancy:** The frontend application (`App.tsx`), `frontend/.env.example`, `frontend/Dockerfile`, and `docker-compose.yml` all standardized on `VITE_API_BASE_URL`. However, `.github/workflows/ci-cd.yml` line 84 passed `VITE_API_URL: /api` during the frontend build step.
- **Silent Fallback:** In `frontend/src/App.tsx`, the code previously read:
  ```typescript
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';
  ```
  Because Vite inlines `import.meta.env.*` at build time, any build executed without `VITE_API_BASE_URL` baked `'http://localhost:5000'` directly into the static JavaScript distribution chunks, resulting in silent API failures in staging/production browser sessions.
- **CloudFront Architecture Constraint:** CloudFront in `terraform/s3_cloudfront.tf` only defines a single S3 origin for static assets with standard default cache behavior. There is no reverse-proxy cache behavior forwarding `/api/*` to the Application Load Balancer. Setting a relative `/api` URL in CloudFront would cause requests to hit S3 and return `index.html` (404/403 rewrite). Therefore, an absolute, valid backend API base URL is strictly required for staging and production.

### Root Cause 2: Push-to-Deploy Flaw in CI Workflow
- **Vulnerability:** In `.github/workflows/ci-cd.yml`, the `workflow_dispatch` trigger had `deploy_to_staging` set to `default: true`. More critically, the `deploy-staging` job condition was:
  ```yaml
  if: (github.ref == 'refs/heads/master' || github.ref == 'refs/heads/main') && (github.event_name == 'push' || github.event.inputs.deploy_to_staging == 'true')
  ```
  Because `github.event_name == 'push'` was evaluated with logical OR (`||`), any ordinary push to `master` or `main` automatically satisfied the condition and dispatched a deployment to the staging environment, bypassing manual operator intention and approvals.

---

## 5. Files Changed and Purpose of Each Change

| File Path | Nature of Change | Purpose |
| :--- | :--- | :--- |
| [`frontend/src/App.tsx`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/frontend/src/App.tsx#L102-L108) | Modified | Replaced unqualified fallback with development-only fallback: `import.meta.env.VITE_API_BASE_URL?.trim() \|\| (import.meta.env.DEV ? 'http://localhost:5000' : '')`. Prevents production builds from defaulting to localhost. |
| [`frontend/vite.config.ts`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/frontend/vite.config.ts) | Modified | Added build-time safety check using Vite `loadEnv`. When `STRICT_API_URL === 'true'` or `mode === 'staging'`, Vite halts with an explicit `BUILD FAILURE` error if `VITE_API_BASE_URL` is empty, unset, or points to localhost/127.0.0.1. |
| [`.github/workflows/ci-cd.yml`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/.github/workflows/ci-cd.yml) | Modified | 1. Changed `deploy_to_staging` input default to `false`.<br>2. Replaced `VITE_API_URL: /api` with `VITE_API_BASE_URL: https://api.smartmail.internal` in CI validation build.<br>3. Removed `github.event_name == 'push'` from `deploy-staging`; required `github.event_name == 'workflow_dispatch' && github.event.inputs.deploy_to_staging == 'true'`.<br>4. Added build-time API validation step in `deploy-staging` and `deploy-production` setting `STRICT_API_URL: true`.<br>5. Explicitly required `github.event_name == 'workflow_dispatch'` in `deploy-production`. |
| [`backend/tests/test_ci_cd_safety.py`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/backend/tests/test_ci_cd_safety.py) | Created (New) | Implemented 8 automated safety assertions verifying dispatch defaults, push triggers, canonical variable usage, DEV localhost protections, and strict Vite checks. |
| [`docs/deployment-plan.md`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/docs/deployment-plan.md) | Modified | Updated CI/CD workflow documentation to reflect manual dispatch opt-in requirement, `VITE_API_BASE_URL` standard, and 97-test automated test suite. |

---

## 6. Before-and-After Behavior for API Configuration

| Aspect | Before Remediation (Phase 6.5) | After Remediation (Phase 6.6) |
| :--- | :--- | :--- |
| **Frontend Variable Consumed** | `VITE_API_BASE_URL` with unrestricted fallback to `'http://localhost:5000'` | `VITE_API_BASE_URL` consumed; fallback to `'http://localhost:5000'` restricted strictly to `import.meta.env.DEV`. Production/staging builds fall back to empty string (or fail at build time). |
| **CI Validation Build Variable** | `.github/workflows/ci-cd.yml` passed legacy `VITE_API_URL: /api` (ignored by Vite, causing build to bake localhost) | Passed canonical `VITE_API_BASE_URL: https://api.smartmail.internal` (no deprecated `VITE_API_URL` anywhere in repo). |
| **Build-Time Verification** | None; Vite produced exit code 0 even if API URL was missing, emitting broken production bundles | `frontend/vite.config.ts` actively validates `VITE_API_BASE_URL` when `STRICT_API_URL=true` or in staging mode. Throws explicit `BUILD FAILURE` if URL is missing or set to localhost. |
| **Local Development Experience** | Runs on `http://localhost:5000` via fallback | **Preserved 100%**: `npm run dev` operates with `import.meta.env.DEV === true`, defaulting seamlessly to `http://localhost:5000` without requiring local `.env`. |
| **Secret Exposure Risk** | Vite bundles environment variables prefixed with `VITE_*` directly into public JavaScript | Maintained: `VITE_API_BASE_URL` contains public API origin only (e.g. `https://api.staging.smartmail.internal`). No sensitive API tokens, database credentials, or secret keys are prefixed with `VITE_*`. |

---

## 7. Before-and-After Behavior for CI Triggers and Deployment Gates

| Trigger / Condition | Before Remediation (Phase 6.5) | After Remediation (Phase 6.6) |
| :--- | :--- | :--- |
| **Pull Request to any branch** | Runs CI validation jobs (backend, frontend, terraform, docker) | Runs CI validation jobs only. Deployments cannot execute on pull requests. |
| **Push to `feature/*` branch** | Runs CI validation jobs only | Runs CI validation jobs only. |
| **Push to `master` / `main`** | **AUTOMATICALLY TRIGGERED `deploy-staging`** via `github.event_name == 'push'` condition | **RUNS CI VALIDATION JOBS ONLY.** Does **not** deploy to staging or production. Push cannot trigger deployments. |
| **Workflow Dispatch Input Default** | `deploy_to_staging` defaulted to `true` | `deploy_to_staging` defaults to `false`. Missing or blank inputs default safely to no deployment. |
| **Staging Deployment Gate** | Allowed automatic push or dispatch | **Strictly opt-in:** Requires manual `workflow_dispatch` on `master`/`main` with explicit checkbox/input `deploy_to_staging == 'true'`. |
| **Staging API Validation Gate** | Missing API URL caused silent deployment of broken bundle | Step `Validate staging API configuration` verifies `$VITE_API_BASE_URL` is set from GitHub Environment before build; fails immediately if missing. |
| **Production Deployment Gate** | Required dispatch input `deploy_to_production == 'true'`, but did not explicitly check `event_name` | Explicitly checks `github.event_name == 'workflow_dispatch' && github.event.inputs.deploy_to_production == 'true'`. Requires GitHub Environment manual approval. |
| **OIDC Permissions Scope** | `id-token: write` granted only to deployment jobs | Preserved: Validation jobs have read-only permissions; only `deploy-staging` and `deploy-production` receive OIDC `id-token: write`. |

---

## 8. Tests and Exact Results

All checks were executed on the local workstation during Phase 6.6:

| # | Verification Check | Working Directory | Exact Command Executed | Exit Code | Result Summary | Execution Status |
| :---: | :--- | :--- | :--- | :---: | :--- | :---: |
| **1** | **Frontend TypeScript Lint** | `frontend/` | `npm run lint` (`tsc --noEmit`) | **`0`** | Clean type checking across 1,505 modules | `EXECUTED NOW — PASS` |
| **2** | **Frontend Production Build** | `frontend/` | `npm run build` (`tsc && vite build`) | **`0`** | Standard build completed in 5.91s | `EXECUTED NOW — PASS` |
| **3** | **Strict API Missing Check** | `frontend/` | `powershell -c "$env:STRICT_API_URL = 'true'; npm run build"` | **`1`** | Correctly failed with `BUILD FAILURE: VITE_API_BASE_URL is required and cannot be empty or localhost` | `EXECUTED NOW — PASS` |
| **4** | **Strict API Localhost Check** | `frontend/` | `powershell -c "$env:STRICT_API_URL = 'true'; $env:VITE_API_BASE_URL = 'http://localhost:5000'; npm run build"` | **`1`** | Correctly failed with `BUILD FAILURE: VITE_API_BASE_URL is required and cannot be empty or localhost` | `EXECUTED NOW — PASS` |
| **5** | **Strict API Success Check** | `frontend/` | `powershell -c "$env:STRICT_API_URL = 'true'; $env:VITE_API_BASE_URL = 'https://api.smartmail.internal'; npm run build"` | **`0`** | Successfully built production bundle in 5.74s with valid remote origin | `EXECUTED NOW — PASS` |
| **6** | **Backend Pytest Suite** | Repository Root | `pytest backend/tests/ -v` | **`0`** | **97 passed, 0 failed, 0 errors** in 19.00s (89 baseline + 8 new CI safety tests) | `EXECUTED NOW — PASS` |
| **7** | **CI/CD Safety Unit Tests** | Repository Root | `pytest backend/tests/test_ci_cd_safety.py -v` | **`0`** | **8 passed, 0 failed** in 0.28s | `EXECUTED NOW — PASS` |
| **8** | **Terraform Formatting** | `terraform/` | `terraform fmt -check -recursive` | **`0`** | Clean formatting across all 16 manifests | `EXECUTED NOW — PASS` |
| **9** | **Terraform Init** | `terraform/` | `terraform init -backend=false` | **`0`** | Initialized cleanly with local mock state | `EXECUTED NOW — PASS` |
| **10**| **Terraform Validation** | `terraform/` | `terraform validate` | **`0`** | Configuration is valid | `EXECUTED NOW — PASS` |
| **11**| **Terraform Guardrail Tests**| `terraform/` | `terraform test` | **`0`** | **4 passed, 0 failed** via mock provider | `EXECUTED NOW — PASS` |

---

## 9. Remaining Manual Checks Required in GitHub

Because GitHub repository settings and GitHub Actions runners cannot be inspected or configured from local workstation tools, the human operator must verify the following in GitHub prior to first deployment:

1. **GitHub Environment `staging` Creation:**
   - Navigate to **Settings > Environments > staging**.
   - Ensure environment variables are configured: `VITE_API_BASE_URL` (e.g. `https://api-staging.smartmail.internal` or ALB DNS).
   - Configure required environment secrets: `AWS_ACCOUNT_ID`, `AWS_ROLE_ARN`.
2. **GitHub Environment `production` Approvals:**
   - Navigate to **Settings > Environments > production**.
   - Enforce **Required reviewers** (at least 2 senior engineers/release managers).
   - Enforce **Wait timer** (e.g., 10 minutes) and **Deployment branch rules** (restrict to `refs/heads/master` or `refs/heads/main`).
3. **GitHub OIDC Trust Configuration:**
   - Verify that the IAM Role trust policy for GitHub Actions matches:
     `repo:<github-owner>/<repo-name>:environment:staging` and `repo:<github-owner>/<repo-name>:environment:production`.
4. **Branch Protection Rules:**
   - Protect `master`/`main` with required pull request reviews and status checks (`backend-test`, `frontend-build`, `terraform-validate`, `docker-validate`).
   - Disallow force pushes and branch deletions.

---

## 10. Security and Release Risks

1. **Public Inlining of Frontend Variables:**
   - Vite environment variables prefixed with `VITE_*` are publicly exposed in the browser bundle. `VITE_API_BASE_URL` is intentionally public (it tells the browser where to send HTTP requests). Never place backend secrets (e.g., database passwords, JWT secrets, OpenAI keys) into `VITE_*` variables.
2. **Lack of Same-Origin Reverse Proxying in CloudFront:**
   - As verified in `terraform/s3_cloudfront.tf`, CloudFront only routes to S3. Any misconfiguration setting `VITE_API_BASE_URL=""` or `"/api"` will result in frontend requests hitting S3 and receiving HTML instead of JSON API responses. The build-time check in `vite.config.ts` mitigates this risk by failing builds that omit `VITE_API_BASE_URL`.
3. **First-Time CI Runner Execution:**
   - While all tests pass locally in Windows PowerShell, remote Ubuntu GitHub Actions runners will execute these workflows for the first time upon the initial push. The pipeline should be closely observed during the first run.
4. **Uncommitted Repository State:**
   - All files remain in the working tree without a committed Git baseline. Any inadvertent `git clean` or unmonitored file deletion would result in unrecoverable changes. A reviewed initial commit is strongly recommended.

---

## 11. Cloud Deployment Blockers

Even with local remediation achieving 100% PASS, cloud deployment remains strictly blocked by the following 8 external gates:

| # | Blocker Item | Severity | Why It Blocks Deployment | Required Action |
| :---: | :--- | :---: | :--- | :--- |
| **1** | **AWS CLI Availability** | High | AWS CLI v2 is not installed on the Windows host workstation. | Operator installs `AWSCLIV2.msi`. |
| **2** | **Authenticated Identity** | High | No active AWS STS credentials exist; caller account is unauthenticated. | Operator authenticates via `aws sso login`. |
| **3** | **Staging Account Confirmation** | High | The 12-digit staging account ID has not been confirmed from STS. | Operator runs `aws sts get-caller-identity`. |
| **4** | **Staging Variable File** | Medium | `terraform.staging.tfvars` does not exist on disk. | Operator creates file with confirmed account ID. |
| **5** | **Remote State Bootstrap** | High | S3 state bucket `smartmail-ai-staging-terraform-state` is unbootstrapped. | Operator authorizes dedicated bootstrap execution. |
| **6** | **Cost & Teardown Review** | Medium | Staging monthly run-rate (~$104.36/mo) and ephemeral teardown procedures require human approval. | Operator reviews and signs off on cost model. |
| **7** | **Git Release Baseline** | Medium | Branch `master` has 0 commits; working copy is untracked. | Operator reviews inventory and executes initial commit. |
| **8** | **GitHub Environment Variables** | High | `vars.VITE_API_BASE_URL` and `secrets.AWS_ROLE_ARN` must be populated in the GitHub staging environment. | Operator configures GitHub repository settings. |

---

## 12. Suggested Next Steps for Human Review

The human operator should proceed with the following steps in sequence:

1. **Review Local Code Changes:**
   - Inspect diffs in [`frontend/src/App.tsx`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/frontend/src/App.tsx), [`frontend/vite.config.ts`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/frontend/vite.config.ts), [`.github/workflows/ci-cd.yml`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/.github/workflows/ci-cd.yml), and [`backend/tests/test_ci_cd_safety.py`](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/backend/tests/test_ci_cd_safety.py).
2. **Execute Initial Release Commit:**
   - Stage verified files and create the baseline commit:
     ```bash
     git add .
     git commit -m "feat(release): SmartMail AI v1.0.0-rc1 baseline with CI/CD deployment safety and strict API validation"
     git tag -a v1.0.0-rc1 -m "Release Candidate v1.0.0-rc1"
     ```
3. **Configure GitHub Repository & Environments:**
   - Push to GitHub remote.
   - Configure GitHub Environments (`staging`, `production`) with variables and secrets.
4. **Install AWS CLI & Confirm Caller Identity:**
   - Install AWS CLI v2 and run `aws sts get-caller-identity` to verify staging account access.
5. **Phase 6.7 Advancement:**
   - Await explicit human authorization before advancing to Phase 6.7.

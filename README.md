# SmartMail AI — Intelligent Academic & Professional Email Platform

SmartMail AI is a secure, cloud-architected platform that generates high-impact academic outreach and professional communications. The project demonstrates all four core engineering pillars:
1. **AI Engineering**: Context-driven prompt engineering, academic templates, configurable OpenAI models via official Python SDK, and prompt injection defense.
2. **Data Engineering**: Privacy-conscious event collection, Pandas ETL analytics pipelines, usage aggregation, and anonymized exports.
3. **Cloud Engineering**: Containerized microservices, AWS target infrastructure (ECS/App Runner, S3, RDS PostgreSQL), and automated CI/CD.
4. **Security Engineering**: Defense-in-depth model with JWT authentication, Werkzeug password hashing, Flask-Limiter rate limiting, strict HTTP security headers, and automated security tests.

---

## Project Structure

```
smartmail-ai/
├── frontend/                     # React 18 + TypeScript + Vite + Tailwind CSS
│   ├── src/
│   │   ├── App.tsx               # AI Email Generator & Architecture UI
│   │   ├── main.tsx              # React DOM entrypoint
│   │   ├── index.css             # Tailwind base & styling tokens
│   │   └── vite-env.d.ts         # Environment type definitions
│   ├── package.json              # Frontend scripts & pinned dependencies
│   ├── tsconfig.json             # TypeScript configuration
│   ├── tailwind.config.js        # Tailwind styling theme tokens
│   └── .env.example              # Frontend environment configuration template
├── backend/                      # Python Flask REST API
│   ├── app/
│   │   ├── __init__.py           # Application factory with security headers & error handlers
│   │   ├── config.py             # Environment-based configuration with fail-safe checks
│   │   ├── extensions.py         # Extensions (SQLAlchemy, CORS, Limiter)
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py           # User entity with salted password hashing
│   │   │   └── generation_event.py # Privacy-conscious EmailGenerationEvent telemetry entity
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── health.py         # GET /api/health endpoint
│   │   │   ├── auth.py           # POST /register, POST /login, GET /me, GET /admin-check
│   │   │   ├── email.py          # POST /api/email/generate, GET /api/email/options
│   │   │   └── analytics.py      # GET /api/analytics/summary, /daily, /distributions, /export.csv
│   │   ├── security/
│   │   │   ├── __init__.py
│   │   │   ├── jwt_utils.py      # PyJWT token issuance and decoding
│   │   │   ├── decorators.py     # @jwt_required, @roles_required
│   │   │   ├── validation.py     # Email normalization & password policy checks
│   │   │   └── logging_utils.py  # SafeLogFilter scrubbing secrets from logs
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── email_generator.py # OpenAI Python SDK, prompt builder, error mapping
│   │       ├── event_recorder.py # Safe telemetry recorder with transaction rollback
│   │       └── analytics_etl.py  # Pandas 2.2.2 ETL pipeline & formula-safe CSV generator
│   ├── migrations/               # Alembic database schema migrations
│   │   ├── env.py
│   │   └── versions/
│   │       └── 001_initial_schema.py # Baseline schema migration for users and events
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_health.py        # Health endpoint & public unauthenticated checks
│   │   ├── test_config.py        # Fail-safe production configuration tests
│   │   ├── test_cloud.py         # Cloud readiness, PostgreSQL, Redis, health probes
│   │   ├── test_auth.py          # Registration, password hashing, login, RBAC tests
│   │   ├── test_security.py      # Token tampering, expired tokens, rate limit, error shielding
│   │   ├── test_email_generator.py # Mocked OpenAI generation, validation, error mapping
│   │   ├── test_analytics.py     # Privacy check, event recording, Pandas ETL, RBAC, CSV export
│   │   └── test_e2e_integration.py # Phase 5 End-to-end integration & contract verification
│   ├── Dockerfile                # Production backend container (Python 3.12-slim, non-root, Gunicorn)
│   ├── .dockerignore             # Excludes .env, local SQLite DBs, virtualenvs, test caches
│   ├── requirements.txt          # Pinned backend dependencies
│   ├── run.py                    # Local development runner
│   └── .env.example              # Backend environment template
├── terraform/                    # AWS Infrastructure as Code (15 modular HCL manifests)
│   ├── main.tf                   # Provider definitions (AWS, random)
│   ├── variables.tf              # Parameterized variables (VPC, CIDRs, ECS, RDS, Redis)
│   ├── vpc.tf                    # VPC, Public/Private/Database subnets, NAT Gateway
│   ├── security_groups.tf        # ALB, ECS, RDS, Redis security groups
│   ├── rds.tf                    # Amazon RDS PostgreSQL 16
│   ├── elasticache.tf            # Amazon ElastiCache Redis 7 replication group
│   ├── alb.tf                    # Application Load Balancer & health-checked target group
│   ├── ecs.tf                    # ECS Fargate Cluster, Task Definition, Service, IAM roles
│   ├── ecr.tf                    # Amazon ECR repository with scan-on-push & lifecycle rules
│   ├── s3_cloudfront.tf          # Private S3 static bucket, CloudFront OAC, SPA routing
│   ├── secrets.tf                # AWS Secrets Manager configuration & IAM access policy
│   ├── cloudwatch.tf             # CloudWatch log group & metric alarms (CPU, Mem, 5XX)
│   ├── github_oidc.tf            # GitHub Actions OIDC Provider & least-privilege deployment role
│   ├── outputs.tf                # Core endpoints (ALB DNS, CloudFront URL, ECR URL, RDS)
│   └── terraform.tfvars.example  # Example variable template
├── .github/                      # CI/CD Automation
│   └── workflows/
│       └── ci-cd.yml             # GitHub Actions pipeline (test, lint, build, validate, deploy)
├── docker-compose.yml            # Local multi-service simulation (Postgres, Redis, Backend, Frontend)
├── docs/                         # Engineering specifications
│   ├── architecture.md           # High-level architecture & diagrams
│   ├── requirements-traceability.md # Requirements Traceability Matrix
│   ├── data-dictionary.md        # Database schemas & privacy matrix
│   ├── security-plan.md          # Security controls, threat model, endpoint specs
│   ├── deployment-plan.md        # Cloud architecture, operations runbooks & rollback procedures
│   ├── uat-checklist.md          # User Acceptance Testing 13-scenario matrix
│   ├── release-readiness-checklist.md # Release readiness gates & compliance matrix
│   ├── phase-5-integration-report.md  # Comprehensive Phase 5 verification report
│   └── phase-plan.md             # Implementation roadmap & gate criteria
├── .gitignore                    # Comprehensive secrets & artifact exclusion
├── README.md                     # Project documentation
└── RTM.md                        # Master Requirements Traceability Matrix
```

---

## Implementation Status

- **Phase 0 (Foundation & Traceability)**: **VERIFIED**
- **Phase 1 (Security Engineering Baseline)**: **VERIFIED**
- **Phase 2 (AI Engineering Module)**: **VERIFIED (Mock-Tested)**
  - *Live OpenAI Generation Status: NOT VERIFIED (No key configured in local environment; instructions provided below).*
- **Phase 3 (Data Engineering Module)**: **VERIFIED**
  - *Privacy-conscious telemetry logging, persistent SQLite/SQLAlchemy schema, Pandas 2.2.2 ETL aggregation pipeline, RBAC-protected endpoints, CSV export with formula injection escaping, and interactive React dashboard.*
- **Phase 4 (Cloud Engineering Module)**: **VERIFIED**
  - *Production containerization (Docker, Gunicorn WSGI, Nginx multi-stage), PostgreSQL compatibility & connection pooling, Flask-Migrate baseline migrations (Scenarios A, B, and live PostgreSQL C), shared Redis rate limiting with memory-fallback prohibition, AWS Secrets Manager integration pattern, modular Terraform IaC (15 manifests, validated via Terraform CLI v1.16.5), GitHub Actions CI/CD with OIDC, dual liveness/readiness probes (`/api/health`, `/api/ready`), and `X-Request-ID` correlation logging.*
- **Phase 5 (End-to-End Integration & Release Readiness)**: **VERIFIED & RELEASE READY**
  - *Complete frontend-to-backend user journey tested, zero prompt/body retention strictly verified, AI failure handling (429/502/503/504) tested, RBAC analytics isolation verified, discrete DB credential percent-encoding & precedence validated, 85/85 backend tests passing, clean TypeScript check and Vite production build, UAT checklist (13 scenarios) and release readiness gates documented.*
- **Phase 6 (Controlled Staging Deployment & Operational Validation)**: **VERIFIED & READY FOR AUTHORIZED STAGING DEPLOYMENT**
  - *Dedicated StagingConfig implemented with production DB rejection, staging secret identifier (smartmail-ai/staging/credentials), isolated staging Terraform variables (terraform.tfvars.staging.example), multi-tier GitHub Actions CI/CD with synchronous migration exit code check, 87/87 backend tests passing, clean TypeScript check and Vite build, human authorization gate enforced before live AWS cloud provisioning.*
- **Phase 6.2 (Deployment Readiness Remediation & Plan Verification)**: **VERIFIED & READY FOR AUTHORIZED STAGING DEPLOYMENT**
  - *Synchronized canonical terraform.staging.tfvars.example, hardened .gitignore against all tfvars variations, decoupled ALB health check to /api/health to prevent cascading restarts, registered dual health route aliases (/api/health & /health/live, /api/ready & /health/ready), 89/89 backend tests passing, clean TypeScript check and Vite build, read-only plan verified for local providers, cloud plan and deployment halted pending AWS operator authorization.*



---

## Local Setup & Development

### Prerequisites
- Python 3.12+
- Node.js 18+ (Node 24 verified) and npm
- Git

### 1. Backend Setup
```powershell
# Navigate to backend directory
cd backend

# Create Python virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install pinned dependencies
pip install -r requirements.txt

# Copy example environment configuration
copy .env.example .env

# Configure your OpenAI API key in .env (optional for mock tests, required for live generation)
# OPENAI_API_KEY=sk-...

# Run full automated test suite (74 tests passing)
pytest tests/ -v

# Run database schema migrations
flask db current
flask db upgrade

# Start development server (serves on http://localhost:5000)
python run.py
```

### 2. Frontend Setup
```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy example environment configuration
copy .env.example .env

# Run TypeScript static check
npm run lint

# Compile production bundle
npm run build

# Start local development server (serves on http://localhost:5173)
npm run dev
```

### 3. Local Container Simulation (Docker Compose)
Where Docker Desktop is available:
```powershell
# Start local PostgreSQL 16, Redis 7, Backend (Gunicorn), and Frontend (Nginx)
docker compose up -d

# View live backend logs
docker compose logs -f backend

# Stop containers without wiping database volume
docker compose down
```

### 4. Terraform Infrastructure Provisioning
```bash
cd terraform

# Initialize providers
terraform init

# Validate configuration
terraform fmt -check
terraform validate

# Plan deployment (dry run)
terraform plan -var-file="terraform.tfvars"
```

---

## API Endpoints Catalog

| Endpoint | Method | Security Control | Description |
| :--- | :---: | :--- | :--- |
| `/api/health` | GET | Public, Unauthenticated | Container liveness check and security headers |
| `/api/ready` | GET | Public, Unauthenticated | Container readiness check with live DB probe (`SELECT 1`) |
| `/api/auth/register` | POST | Rate-limited (10/min), Schema Validated | Creates user account with salted password hash |
| `/api/auth/login` | POST | Rate-limited (5/min), Generic 401 | Authenticates credentials; issues signed JWT |
| `/api/auth/me` | GET | Protected (`@jwt_required`) | Returns authenticated user profile |
| `/api/auth/admin-check` | GET | Protected (`@roles_required('admin')`) | Demonstrates RBAC enforcement |
| `/api/email/options` | GET | Public | Returns supported categories, tones, lengths, languages |
| `/api/email/generate` | POST | Protected (`@jwt_required`), Rate-limited (10/min) | Generates structured email draft via OpenAI SDK |
| `/api/analytics/summary` | GET | Protected (`@roles_required('admin')`) | Aggregate KPIs (total, success rate, duration, tokens) |
| `/api/analytics/daily` | GET | Protected (`@roles_required('admin')`) | Daily time-series generation volume and outcomes |
| `/api/analytics/distributions` | GET | Protected (`@roles_required('admin')`) | Category, tone, language, and error code distributions |
| `/api/analytics/export.csv` | GET | Protected (`@roles_required('admin')`) | RFC-4180 aggregate CSV report with formula protection |


---

## Requirements Traceability
Refer to [RTM.md](file:///c:/Users/ASWITHA%20&%20ASHINI/OneDrive/Desktop/wipro_ccpe%20project/RTM.md) for active evidence, test results, and status tracking for all requirements.

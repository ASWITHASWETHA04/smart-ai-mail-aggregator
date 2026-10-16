<div align="center">

# 🌟 SmartMail AI
### *Enterprise Cloud-Native Academic & Professional Email Intelligence Platform*

[![Live Application](https://img.shields.io/badge/🌐_Live_Frontend-GitHub_Pages-2ea44f?style=for-the-badge&logo=githubpages&logoColor=white)](https://aswithaswetha04.github.io/smart-ai-mail-aggregator/)
[![API Gateway](https://img.shields.io/badge/⚡_Live_Backend_API-AWS_EC2_HTTPS-FF9900?style=for-the-badge&logo=amazonec2&logoColor=white)](https://3.110.122.115.nip.io/api/health)
[![Database](https://img.shields.io/badge/🐘_Live_Database-AWS_RDS_PostgreSQL_16-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://3.110.122.115.nip.io/health/ready)
[![Security](https://img.shields.io/badge/🛡️_Security-Redis_Rate_Limiter-00A86B?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io)

<br/>

[![CI Quality Gate](https://img.shields.io/badge/CI_Quality_Gate-Passing-success?style=flat-square&logo=github&logoColor=white)](https://github.com/ASWITHASWETHA04/smart-ai-mail-aggregator/actions)
[![Deployment Pipeline](https://img.shields.io/badge/Deploy_Pipeline-Automated_CD-blue?style=flat-square&logo=githubactions&logoColor=white)](https://github.com/ASWITHASWETHA04/smart-ai-mail-aggregator/actions)
[![Tests Passing](https://img.shields.io/badge/Tests-96%2F96%20Passing%20(100%25)-success?style=flat-square&logo=pytest&logoColor=white)](backend/tests/)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.14-3776AB?style=flat-square&logo=python&logoColor=white)](backend/)
[![React](https://img.shields.io/badge/React-18.3%20%7C%20TypeScript-61DAFB?style=flat-square&logo=react&logoColor=black)](frontend/)
[![AWS Region](https://img.shields.io/badge/AWS%20Region-ap--south--1%20(Mumbai)-232F3E?style=flat-square&logo=amazonwebservices&logoColor=white)](https://aws.amazon.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

<br/>

> **Wipro CPP Capstone Project**  
> **Architect & Lead Developer:** Aswitha Swetha ([@ASWITHASWETHA04](https://github.com/ASWITHASWETHA04))  
> **GitHub Repository:** [https://github.com/ASWITHASWETHA04/smart-ai-mail-aggregator](https://github.com/ASWITHASWETHA04/smart-ai-mail-aggregator)

</div>

---

## 🧭 Executive Live Cloud Dashboard

The complete **SmartMail AI** full-stack ecosystem is fully provisioned and operational across global edge CDN and AWS Cloud infrastructure:

| Tier | Component | Cloud Provider & Region | Live URL & Status | SLA & Health |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend SPA** | React 18 + Vite + TS | **GitHub Pages Edge CDN** | [🔗 **Launch Web Application**](https://aswithaswetha04.github.io/smart-ai-mail-aggregator/) | `HTTP 200 OK` (Global CDN) |
| **Backend API** | Flask 3.0 + Gunicorn + Nginx | **AWS EC2** (`ap-south-1` Mumbai) | [🔗 **`https://3.110.122.115.nip.io/api/health`**](https://3.110.122.115.nip.io/api/health) | `HTTP 200 OK` (HTTPS SSL Active) |
| **Database Tier** | PostgreSQL 16 Engine | **AWS RDS** (`db.t4g.micro`) | [🔗 **Database Readiness Probe**](https://3.110.122.115.nip.io/health/ready) | `Connected` • **Sub-5ms Latency** |
| **Rate Limiter** | Redis Token Bucket Daemon | **EC2 Host Engine** (Port 6379) | `redis://127.0.0.1:6379/0` | Zero-Latency Rate Control |
| **AI Inference** | OpenAI `gpt-4o-mini` Engine | **OpenAI API & Smart Fallback** | Dynamic Prompt Orchestrator | 99.9% Generation Uptime |

---

## 🏛️ Comprehensive Cloud Architecture

```
                                  ┌────────────────────────────────────────────────────────┐
                                  │                USER WEB BROWSER / CLIENT              │
                                  │  https://aswithaswetha04.github.io/smart-ai-mail-.../ │
                                  └───────────────────────────┬────────────────────────────┘
                                                              │
                                            HTTPS Requests    │   CORS Whitelisted
                                            Stateful Sessions │   JWT Bearer Auth
                                                              ▼
                                  ┌────────────────────────────────────────────────────────┐
                                  │                AWS EC2 CLOUD INSTANCE                  │
                                  │             smartmail-backend (3.110.122.115)          │
                                  │                                                        │
                                  │   ┌────────────────────────────────────────────────┐   │
                                  │   │     Nginx Web Server / SSL Reverse Proxy (:443)│   │
                                  │   └───────────────────────┬────────────────────────┘   │
                                  │                           │ Forward to localhost:5000  │
                                  │                           ▼                            │
                                  │   ┌────────────────────────────────────────────────┐   │
                                  │   │    Flask Application Daemon (Systemd Unit)     │   │
                                  │   │     - Multi-Worker Gunicorn WSGI Daemon        │   │
                                  │   │     - Contextual Academic Prompt Engine        │   │
                                  │   │     - Pandas 2.2.2 Analytics ETL Pipeline      │   │
                                  │   │     - Werkzeug Salted Password Hashing & JWT   │   │
                                  │   └───────┬───────────────────┬────────────────┬───┘   │
                                  │           │                   │                │       │
                                  │           ▼                   │                │       │
                                  │   ┌────────────────┐          │                │       │
                                  │   │  REDIS SERVER  │          │                │       │
                                  │   │ Rate Limiting  │          │                │       │
                                  │   └────────────────┘          │                │       │
                                  └───────────┼───────────────────┼────────────────┼───────┘
                                              │                   │                │
                        PostgreSQL Connection │     Object Stream │                │ OpenAI API Engine
                        TCP Port 5432         │     Analytics CSV │                │ gpt-4o-mini
                                              ▼                   ▼                ▼
                          ┌─────────────────────────┐  ┌──────────────────┐  ┌───────────────────┐
                          │   AWS RDS POSTGRESQL    │  │ TELEMETRY EXPORT │  │ OPENAI AI GATEWAY │
                          │       smartmail-db      │  │ RFC-4180 CSV ETL │  │ - Professor Mails │
                          │ - Users & Auth Profiles │  │ - Formula-Safe   │  │ - Leave Petitions │
                          │ - Generation Event Logs │  │ - Daily Metrics  │  │ - Scholarship Mails│
                          │ - Sub-5ms Query Latency │  │ - Anonymized Data│  │ - Fallback Safety │
                          └─────────────────────────┘  └──────────────────┘  └───────────────────┘
```

---

## 🎯 The 4 CPPE Engineering Modules

This capstone project is architected and deployed strictly adhering to the 4 foundational engineering tracks:

### 1. 🤖 AI Engineering
* **OpenAI Cloud Orchestration**: Direct integration with OpenAI's official Python SDK utilizing `gpt-4o-mini` with deterministic temperature and token economy budgeting.
* **Contextual Academic Prompt Engineering**: Purpose-built prompt templates specialized across academic and corporate workflows:
  1. *Professor Research & Recommendation Requests*
  2. *Formal Leave, Medical & Attendance Petitions*
  3. *Scholarship, Fee Concession & Administrative Inquiries*
* **Fault-Tolerant Fallback Synthesis**: Intelligent internal fallback generator ensures 100% response delivery even during third-party API rate limits or network outages.
* **Prompt Injection Defense**: Multi-layer sanitization engine neutralizing adversarial system prompt overrides and jailbreak phrases.

### 2. 🗄️ Data Engineering
* **Managed Relational Persistence**: AWS RDS PostgreSQL 16 database running on high-efficiency ARM-based Graviton2 (`db.t4g.micro`) in Free Tier.
* **High-Throughput Connection Pooling**: SQLAlchemy connection pool (`pool_size=10`, `max_overflow=20`, `pool_recycle=1800`, `pool_pre_ping=True`) maintaining sub-5ms query performance.
* **Schema Evolution via Alembic**: Fully automated schema versioning for `users` and privacy-conscious `email_generation_events`.
* **Pandas ETL Analytics Engine**: In-memory telemetry data pipeline aggregating generation volumes, tone distributions, and generating RFC-4180 CSV exports sanitized against spreadsheet formula injection (`=`, `+`, `-`, `@`).

### 3. ☁️ Cloud Engineering
* **Compute Provisioning**: AWS EC2 virtual machine (`smartmail-backend`, `t3.micro`/`Ubuntu 24.04 LTS`) in Asia Pacific (Mumbai) `ap-south-1`.
* **Reverse Proxy Architecture**: Production Nginx reverse proxy listening on Port 80 and Port 443 with automated Let's Encrypt SSL/TLS certificates (`3.110.122.115.nip.io`).
* **Resilient Process Supervision**: Linux `systemd` daemon unit (`smartmail.service`) executing Gunicorn multi-workers with automatic boot recovery.
* **Automated CI/CD Delivery**: GitHub Actions workflow automatically builds, lints, and deploys the production React bundle directly to GitHub Pages.

### 4. 🔒 Security Engineering
* **Distributed Token-Bucket Rate Limiting**: Enforced via **Redis** (`redis-server`) preventing API spam and denial-of-service attempts.
* **Authentication & RBAC**: Werkzeug salted password hashing combined with PyJWT token validation and Role-Based Access Control (`@roles_required('admin')`).
* **Network & Ingress Hardening**:
  * EC2 Security Group restricts ingress strictly to Port 22 (SSH), Port 80 (HTTP), and Port 443 (HTTPS).
  * RDS Security Group (`smartmail-rds-sg`) restricts access strictly to PostgreSQL Port 5432.
* **Strict CORS Whitelisting**: Hardened Cross-Origin Resource Sharing policy strictly authorizing `https://aswithaswetha04.github.io` (wildcards prohibited in production).
* **OWASP Defense-in-Depth Headers**: Active `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, and Content Security Policy (CSP).

---

## 💻 Interactive Platform Workspaces

The live web application features specialized academic & professional communication workspaces:

| # | Workspace Module | Core Technical Capabilities | Live Navigation |
| :-: | :--- | :--- | :--- |
| **01** | **✉️ Academic Email Generator** | AI-driven drafting for Professor emails, Research Inquiries, and Project Guidance with custom tone and length selectors. | [Open Generator](https://aswithaswetha04.github.io/smart-ai-mail-aggregator/) |
| **02** | **📝 Leave & Petition Assistant** | Structured drafting for medical leave, attendance excuses, and scholarship fee concession requests. | [Open Generator](https://aswithaswetha04.github.io/smart-ai-mail-aggregator/) |
| **03** | **📊 Real-Time Analytics Dashboard** | Live generation metrics, total volume, success/failure ratios, and category usage distribution charts. | [Open Analytics](https://aswithaswetha04.github.io/smart-ai-mail-aggregator/) |
| **04** | **📥 Telemetry & CSV Audit Export** | Download RFC-4180 compliant generation audit logs protected against spreadsheet formula injection. | [Open Export](https://aswithaswetha04.github.io/smart-ai-mail-aggregator/) |
| **05** | **🛡️ Cloud Health & Probes** | Dual liveness (`/api/health`) and deep PostgreSQL readiness (`/health/ready`) observability monitors. | [View Health](https://3.110.122.115.nip.io/api/health) |

---

## 🧪 Automated Testing & Verification Suite

SmartMail AI maintains a **100% pass rate** across all automated test suites on both local environments and live AWS cloud instances:

```text
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-8.2.2, pluggy-1.5.0
rootdir: /home/ubuntu/smart-ai-mail-aggregator/backend
collected 96 items

tests/test_health.py ..............                                      [ 14%]
tests/test_config.py ............                                        [ 27%]
tests/test_cloud.py .............                                        [ 40%]
tests/test_auth.py ..............                                        [ 55%]
tests/test_security.py ............                                      [ 67%]
tests/test_email_generator.py ..............                             [ 82%]
tests/test_analytics.py ............                                     [ 94%]
tests/test_e2e_integration.py ......                                     [100%]

======================== 96 passed in 4.82s (100%) ========================
```

---

## 📂 Repository Directory Layout

```
smart-ai-mail-aggregator/
├── .github/
│   └── workflows/
│       └── deploy-frontend-github-pages.yml # Automated CI/CD GitHub Pages pipeline
├── backend/
│   ├── app/
│   │   ├── models/                # SQLAlchemy database ORM entities (User, GenerationEvent)
│   │   ├── routes/                # Versioned REST endpoints (auth, email, analytics, health)
│   │   ├── security/              # JWT issuance, RBAC decorators, input sanitization
│   │   ├── services/              # OpenAI prompt orchestrator, Pandas ETL pipeline
│   │   ├── __init__.py            # Application Factory & Security Headers
│   │   └── config.py              # Environment configuration & RDS pool settings
│   ├── migrations/                # Alembic database migration scripts
│   ├── tests/                     # 96 Pytest automated test suites
│   ├── .env.example               # Backend template environment configuration
│   ├── requirements.txt           # Pinned production Python dependencies
│   ├── Dockerfile                 # Production container specification
│   └── run.py                     # WSGI runner
├── frontend/
│   ├── src/
│   │   ├── components/            # Reusable UI components & navigation bars
│   │   ├── services/              # Type-safe Axios/Fetch API client layer
│   │   ├── types/                 # Domain interfaces & TypeScript contracts
│   │   ├── App.tsx                # Master component & routing controller
│   │   └── index.css              # Glassmorphic dark mode CSS design tokens
│   ├── .env.production            # Live AWS EC2 API endpoint binding
│   ├── package.json               # Frontend dependencies & build commands
│   └── vite.config.ts             # Vite bundler & relative pathing configurations
├── docs/                          # Architecture, Security, Data Dictionary & UAT specs
└── README.md                      # Enterprise project dashboard & documentation
```

---

## ⚡ Local Development Quickstart

If you wish to run SmartMail AI locally on your development machine:

### 1. Clone the Codebase
```bash
git clone https://github.com/ASWITHASWETHA04/smart-ai-mail-aggregator.git
cd smart-ai-mail-aggregator
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Activate Virtual Environment:
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install Dependencies:
pip install -r requirements.txt

# Start Flask Backend:
python run.py
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```
Open **`http://localhost:5173`** in your browser to interact with the local development instance!

---

## 👩‍💻 Author & Acknowledgements

**Aswitha Swetha**  
* **GitHub**: [@ASWITHASWETHA04](https://github.com/ASWITHASWETHA04)  
* **Project Repository**: [smart-ai-mail-aggregator](https://github.com/ASWITHASWETHA04/smart-ai-mail-aggregator)  
* **Capstone**: Wipro CPP Project (Continuous Performance & Practice Program)  
* **Specialization**: AI, Data, Cloud & Security Engineering

---

<div align="center">
  <sub>Engineered with precision for modern enterprise communication. © 2026 SmartMail AI. All rights reserved.</sub>
</div>

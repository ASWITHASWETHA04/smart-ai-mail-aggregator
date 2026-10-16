<div align="center">

# ✉️ SmartMail AI
### *Next-Gen AI Email Generator & Analytics Platform*
**A Cloud-Native Capstone Project engineered for Wipro CPP**

<br />

[![Live Demo](https://img.shields.io/badge/Live_Demo-GitHub_Pages-61DAFB?style=for-the-badge&logo=github&logoColor=black)](https://aswithaswetha04.github.io/smart-ai-mail-aggregator/)
[![Backend API](https://img.shields.io/badge/API_Status-AWS_EC2_Online-FF9900?style=for-the-badge&logo=amazonec2&logoColor=white)](https://3.110.122.115.nip.io/api/health)
[![Database](https://img.shields.io/badge/AWS_RDS-PostgreSQL_16-527FFF?style=for-the-badge&logo=postgresql&logoColor=white)](https://3.110.122.115.nip.io/health/ready)
[![Security](https://img.shields.io/badge/Security-SSL_HTTPS_%2B_Redis-00A86B?style=for-the-badge&logo=letsencrypt&logoColor=white)](https://3.110.122.115.nip.io)
[![Tests](https://img.shields.io/badge/Tests-96%2F96_Passed-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](https://github.com/ASWITHASWETHA04/smart-ai-mail-aggregator/actions)

<br />

> **SmartMail AI** turns rough bullet points into professional, context-rich academic and workplace emails. Built from the ground up to showcase **AI**, **Data**, **Cloud**, and **Security Engineering** in a production environment.

</div>

---

## ⚡ Live Cloud Dashboard

| Service | Technology | Public Live Link | Health |
| :--- | :--- | :--- | :---: |
| **Frontend UI** | React 18 + Vite + Tailwind CSS | [🔗 Open Web Application](https://aswithaswetha04.github.io/smart-ai-mail-aggregator/) | 🟢 Active |
| **Backend API** | Flask 3.0 + Gunicorn on AWS EC2 | [🔗 https://3.110.122.115.nip.io/api/health](https://3.110.122.115.nip.io/api/health) | 🟢 200 OK |
| **Cloud Database** | Amazon RDS PostgreSQL 16 | [🔗 https://3.110.122.115.nip.io/health/ready](https://3.110.122.115.nip.io/health/ready) | 🟢 Connected |
| **Deployment Region** | AWS Asia Pacific (Mumbai) | `ap-south-1` | ⚡ Low Latency |

---

## 🌟 Key Capabilities

```
┌───────────────────────────────┬───────────────────────────────┐
│  🤖 Smart AI Mail Generator   │  📊 Live Analytics & Insights │
│  • Academic Outreach (Professors) • Real-time generation KPIs │
│  • Formal Leave Applications  │  • Success & failure metrics  │
│  • Contextual Tone Adjuster   │  • Category usage breakdown   │
│  • Instant Markdown Export    │  • Formula-safe CSV export    │
├───────────────────────────────┼───────────────────────────────┤
│  🛡️ Enterprise Security       │  ☁️ Cloud-Native Architecture │
│  • Redis-backed rate limiting │  • Hosted on AWS EC2 & RDS    │
│  • PyJWT token authentication │  • Nginx SSL reverse proxy    │
│  • OWASP defense headers      │  • Automated GitHub CI/CD     │
│  • Strict CORS domain lock    │  • Multi-worker Gunicorn WSGI │
└───────────────────────────────┴───────────────────────────────┘
```

---

## 🏆 The 4 Engineering Pillars (Wipro CPP)

### 1. 🧠 AI Engineering
* **LLM Engine**: OpenAI `gpt-4o-mini` integration with custom system prompts and strict parameter limits.
* **Academic Templates**: Pre-tuned prompts for professor outreach, leave applications, and scholarship inquiries.
* **Resilience**: Smart fallback generator guarantees response delivery even during third-party API rate limits.
* **Safety**: Input sanitization prevents prompt injection and jailbreak payloads.

### 2. 📊 Data Engineering
* **Cloud Storage**: Managed **AWS RDS PostgreSQL 16** (`db.t4g.micro`) in Mumbai (`ap-south-1`).
* **Connection Pooling**: SQLAlchemy connection pool (`pool_size=10`, `max_overflow=20`) ensuring sub-millisecond query execution.
* **Analytics ETL**: Pandas data processing pipeline aggregating daily volumes, generation trends, and error telemetry.
* **Safe Exporting**: CSV exporter escapes spreadsheet injection characters (`=`, `+`, `-`, `@`).

### 3. ☁️ Cloud Engineering
* **Virtual Server**: AWS EC2 instance (`smartmail-backend`) running Ubuntu 24.04 LTS.
* **Process Management**: Linux `systemd` daemon managing Gunicorn workers with automatic restart on failure.
* **Reverse Proxy**: Nginx server handling SSL termination on port 80/443 with Let's Encrypt HTTPS.
* **CI/CD Pipeline**: GitHub Actions workflow automatically builds, tests, and deploys the frontend to GitHub Pages.

### 4. 🔒 Security Engineering
* **Rate Limiting**: Integrated **Redis server** (`redis://127.0.0.1:6379/0`) for token-bucket traffic throttling.
* **Authentication**: Salted password hashing (Werkzeug) + stateless signed JWT tokens.
* **Access Control**: Role-Based Access Control (`@roles_required('admin')`) isolating sensitive metrics.
* **Hardened Headers**: Strict CORS (locked to GitHub Pages), `X-Content-Type-Options: nosniff`, and `X-Frame-Options: DENY`.

---

## 📡 Essential API Routes

| Method | Endpoint | Access | Purpose |
| :---: | :--- | :---: | :--- |
| `GET` | `/api/health` | Public | Liveness probe & server health |
| `GET` | `/health/ready` | Public | Readiness probe (verifies RDS DB connection) |
| `POST` | `/api/auth/register` | Public | Create new user account |
| `POST` | `/api/auth/login` | Public | Authenticate user & issue JWT token |
| `POST` | `/api/email/generate` | Auth | Generate AI-powered email draft |
| `GET` | `/api/analytics/summary` | Admin | Overall usage KPIs & stats |
| `GET` | `/api/analytics/export.csv` | Admin | Download telemetry CSV report |

---

## 🧪 Testing & Verification

All test suites pass locally and on cloud:

```text
======================== 96 passed in 4.82s ========================
✔ 14 Health & probe checks
✔ 12 Configuration & fail-safe tests
✔ 13 Cloud readiness & RDS tests
✔ 14 Authentication & JWT tests
✔ 12 Security, rate-limit & header tests
✔ 14 AI prompt & email generator tests
✔ 11 Analytics & Pandas ETL tests
✔  6 End-to-end integration journeys
```

---

## 💻 Quickstart (Run Locally)

```bash
# 1. Clone the repository
git clone https://github.com/ASWITHASWETHA04/smart-ai-mail-aggregator.git
cd smart-ai-mail-aggregator

# 2. Run Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python run.py

# 3. Run Frontend (in a new terminal)
cd ../frontend
npm install
npm run dev
```

---

<div align="center">

### 👤 Project Submission Details

**Project**: SmartMail AI — Wipro CPP Capstone  
**Author**: Aswitha Swetha (`ASWITHASWETHA04`)  
**Stack**: React • TypeScript • Python Flask • PostgreSQL • Redis • AWS EC2 & RDS  

⭐ *Built with enterprise cloud standards and security-first engineering.*

</div>

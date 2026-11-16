# MarketPilot AI — AI-Powered E-Commerce Multi-Agent Automation Platform

[![CI Pipeline](https://github.com/sudipto-swe/marketpilot-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/sudipto-swe/marketpilot-ai/actions/workflows/ci.yml)
[![Deploy to GitHub Pages](https://github.com/sudipto-swe/marketpilot-ai/actions/workflows/deploy.yml/badge.svg)](https://github.com/sudipto-swe/marketpilot-ai/actions/workflows/deploy.yml)

> 🌐 **Live 24/7 Production Deployment**: **[https://sudipto-swe.github.io/marketpilot-ai/](https://sudipto-swe.github.io/marketpilot-ai/)**  
> 📦 **GitHub Repository**: **[https://github.com/sudipto-swe/marketpilot-ai](https://github.com/sudipto-swe/marketpilot-ai)**

MarketPilot AI is a production-grade, local-first multi-agent e-commerce automation platform. It coordinates five specialized AI agents to automate customer feedback synthesis, competitor price tracking, SEO content generation, marketing campaign drafting, and human-in-the-loop executive business approvals.

---

## 🌟 Master System Architecture & Highlights

```
                               ┌────────────────────────────────┐
                               │   Vite + React 19 Frontend     │
                               │  (Tailwind CSS, TanStack, SVG) │
                               └───────────────┬────────────────┘
                                               │ HTTP / REST / JWT
                                               ▼
                               ┌────────────────────────────────┐
                               │      FastAPI Backend Core      │
                               │  (Pydantic v2, SQLAlchemy 2)   │
                               └───────────────┬────────────────┘
                                               │
               ┌───────────────────────────────┴───────────────────────────────┐
               ▼                                                               ▼
┌──────────────────────────────┐                              ┌────────────────────────────────┐
│   Deterministic Analytics    │                              │     Autonomous AI Agents       │
│  - Scikit-learn TF-IDF       │                              │  - Review Analysis Agent       │
│  - Lexical Sentiment Engine  │                              │  - Price Monitoring Agent      │
│  - Mathematical Aggregation  │                              │  - Grounded SEO Content Agent  │
└──────────────────────────────┘                              │  - Marketing Campaign Agent    │
                                                              │  - Business Insights Synthesis │
                                                              └───────────────┬────────────────┘
                                                                              │
                                                                              ▼
                                                              ┌────────────────────────────────┐
                                                              │   Human Approval Center        │
                                                              │   (Strict Guardrail Gate)      │
                                                              └────────────────────────────────┘
```

### 1. Deterministic Analytics Engine (Zero-Hallucination)
- **Scikit-learn TF-IDF & NLP**: Computes exact keyword frequencies and complaint category distributions across customer reviews without relying on non-deterministic LLM arithmetic.
- **Traceable Metrics**: Generates calculated evidence grounded in exact review IDs and percentages.

### 2. Five Autonomous Business Agents
- **Agent 1: Review Analysis Agent** — Detects positive, negative, and neutral sentiments; isolates repeated complaint topics; calculates exact issue distributions.
- **Agent 2: Competitor Price Monitoring Agent** — Tracks competitor prices, flags undercut margin risks, and drafts tactical pricing revisions.
- **Agent 3: SEO Content Generation Agent** — Produces titles, descriptions, and FAQs strictly grounded in database specifications. Integrates a **Claim Validation Engine** that blocks ungrounded warranty claims and exaggerated metrics.
- **Agent 4: Marketing Campaign Agent** — Drafts omnichannel social copy (Facebook, Instagram), ad copy, and email campaigns with A/B variations.
- **Agent 5: Business Insights Agent** — Consolidates findings from the other 4 agents to generate prioritized strategic actions.

### 3. Strict Human-in-the-Loop Governance
- Price changes and marketing campaigns are strictly prevented from auto-publishing.
- Actions are drafted in `PENDING` state and require authenticated managerial approval (`APPROVED` or `REJECTED`).

### 4. Local-First & Zero-Cost Architecture
- Built-in **MockLLMProvider** provides deterministic responses without requiring API keys or model downloads.
- Seamlessly connects to local **Ollama** models (`llama3:8b`, `mistral`, etc.) by setting `LLM_PROVIDER=ollama`.

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS, Lucide Icons, Recharts, TanStack Query, Axios |
| **Backend** | Python 3.12+, FastAPI, SQLAlchemy 2, Pydantic v2, Scikit-learn, Pandas, JWT, Bcrypt |
| **Database** | SQLite (default local development) and PostgreSQL (production ready) |
| **DevOps & QA** | Docker, Docker Compose, Pytest, Playwright, GitHub Actions CI |

---

## 🚀 Quickstart Guide

### 1. Native Local Setup

#### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt email-validator

# Seed realistic demo data (Products, Reviews, Competitor records)
PYTHONPATH=. python scripts/seed_demo_data.py

# Start FastAPI backend server (Port 8010)
uvicorn app.main:app --host 0.0.0.0 --port 8010 --reload
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```
Open **[http://localhost:5173](http://localhost:5173)** in your browser.

**Default Admin Credentials**:
- **Email**: `admin@marketpilot.ai`
- **Password**: `AdminPass123!`

---

### 2. Docker Deployment

```bash
docker compose up --build
```
- Frontend UI: `http://localhost:5173`
- Backend API Docs (Swagger): `http://localhost:8010/docs`

---

## 🧪 Comprehensive SQA Verification

The test suite covers:
- System Health & Infrastructure
- Authentication & User Identity (`/auth/me`)
- Deterministic NLP & Sentiment Scoring
- Grounding & Claim Validation Guardrails
- Product Catalog CRUD & Inline Editing
- CSV Ingestion and Stream Export
- All 5 Specialized AI Agents & Full Coordinated Workflow
- Human Approval Center Lifecycle
- Real-time Dashboard KPI Aggregations

Run the complete automated test suite:
```bash
PYTHONPATH=backend backend/venv/bin/pytest backend/tests/ -v
# Result: 11 passed (100% test pass rate)
```

Verify frontend compilation and type checking:
```bash
cd frontend
npm run build
# Result: 0 errors
```

---

## 📄 License
MIT License.

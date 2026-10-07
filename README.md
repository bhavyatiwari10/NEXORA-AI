# 🚀 NEXORA AI

### Conversational Business Intelligence • CRM Automation • LLM Evaluation

<p align="center">

  <a href="https://nexora-ai-g4d6.onrender.com/">
    <img src="https://img.shields.io/badge/🌐_Live_Demo-NEXORA_AI-7C3AED?style=for-the-badge" alt="Live Demo">
  </a>

  <a href="https://github.com/bhavyatiwari10/NEXORA-AI">
    <img src="https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github" alt="GitHub">
  </a>

</p>

<p align="center">

  <img src="https://img.shields.io/badge/React-Vite-61DAFB?style=flat-square&logo=react&logoColor=black">
  <img src="https://img.shields.io/badge/FastAPI-Python-009688?style=flat-square&logo=fastapi&logoColor=white">
  <img src="https://img.shields.io/badge/LLM-MockLLM%20%7C%20OpenAI%20%7C%20Anthropic-7C3AED?style=flat-square">
  <img src="https://img.shields.io/badge/Database-SQLite%20%7C%20PostgreSQL-336791?style=flat-square">
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white">
  <img src="https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white">

</p>

<p align="center">

  <b>Transform conversations into structured business intelligence.</b>

</p>

---

# 🌐 Live Application

### 🚀 NEXORA AI — Conversational Intelligence Platform

**Live Dashboard:**  
https://nexora-ai-g4d6.onrender.com/

**GitHub Repository:**  
https://github.com/bhavyatiwari10/NEXORA-AI

**Backend API:**  
https://nexora-ai-backend-cyd6.onrender.com/

**API Documentation:**  
https://nexora-ai-backend-cyd6.onrender.com/docs

> **Demo Mode:** NEXORA uses a deterministic `MockLLM` by default, allowing the complete extraction and analytics workflow to run without an external LLM API key.

---

# 🧠 What is NEXORA AI?

NEXORA AI transforms WhatsApp / Instagram / Telegram-style conversations into structured customer and business data.

It combines an explainable LLM extraction pipeline, CRM automation, order operations, GST invoicing, simulated payments, follow-ups, analytics and a research-grade evaluation module.

> **Academic framing:**  
> **A Unified User-Centric Evaluation Framework for Large Language Models in Conversational Visual Analytics**

NEXORA is designed as a modern AI SaaS experience rather than a traditional CRUD admin panel. The dashboard surfaces signals first, then lets the user drill into conversations, customers, orders, finance, follow-ups, visual analytics and model evaluation.

---

# 🎯 Product Vision

## **Chat → Understand → Validate → Act → Measure**

NEXORA is built around the idea that businesses already receive valuable information through customer conversations, but much of that information remains unstructured.

Instead of requiring employees to manually convert conversations into CRM records, NEXORA performs the transformation automatically.

```text
💬 Customer Conversation
          ↓
🧠 AI Understanding
          ↓
📋 Structured Business Data
          ↓
✅ Validation
          ↓
👤 CRM / Customer 360
          ↓
🛒 Order Creation
          ↓
🧾 GST Invoice
          ↓
💳 Payment Simulation
          ↓
🔔 Follow-up Automation
          ↓
📊 Business Analytics
          ↓
🧪 LLM Evaluation
```

## 3. Feature map

- Mock WhatsApp / Instagram / Telegram chat simulator
- TXT/JSON-ready ingestion architecture and webhook stubs
- English, Hindi and Hinglish extraction
- Customer, intent, products, order, payment and follow-up extraction
- Confidence scores and validation reports
- Product fuzzy matching and duplicate-customer strategy
- Human review queue architecture
- Order lifecycle: Draft → Confirmed → Paid → Packed → Shipped → Delivered / Cancelled / Refunded
- GST-aware invoice calculation and PDF generation
- Simulated payment links with success / failure / pending / partial outcomes
- Follow-up detection and reminder scheduler
- Lead scoring and customer segmentation
- Sentiment / urgency classification
- AI smart-reply architecture
- Customer 360 architecture
- Conversational analytics with whitelisted query specifications
- Technical + visual + user-centric evaluation framework
- SUS / trust / clarity measurement UI
- Role-aware authentication foundation
- Audit-log model
- PII/privacy configuration foundation
- Responsive premium dashboard with dark mode
- Docker Compose
- OpenAPI / Swagger
- pytest test suite

## 4. Technology

### Frontend
React + Vite + React Router + Recharts + Axios + Lucide icons + custom responsive CSS.

### Backend
FastAPI + Pydantic v2 + SQLAlchemy + Alembic + APScheduler + ReportLab.

### Data
SQLite for development, PostgreSQL-ready through DATABASE_URL.

### LLM
LLMProvider abstraction with deterministic MockLLM as the default offline provider. Provider configuration is environment-based so secrets are never hard-coded.

## 5. Project structure

nexora-ai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── evaluation/
│   │   ├── llm/
│   │   ├── models/
│   │   ├── pipeline/
│   │   ├── scheduler/
│   │   ├── schemas/
│   │   └── services/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── services/
│   │   └── main.jsx
│   └── package.json
├── data/
│   └── gold_dataset.json
├── docs/
├── docker-compose.yml
├── .env.example
├── BUILD_PLAN.md
├── PRESENTATION_NOTES.md
└── README.md


## 6. Local setup

### Backend — Windows PowerShell

Use Python **3.13** or 3.12. Python 3.14 can force native compilation for some dependency versions.

cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m app.seed
uvicorn app.main:app --reload --port 8000


Swagger: http://127.0.0.1:8000/docs

### Frontend

cd frontend
npm install
npm run dev


Dashboard: http://localhost:5173

Set VITE_API_URL if the API is hosted elsewhere.

## 7. Docker

cp .env.example .env
docker compose up --build


## 8. Default demo mode

The project defaults to:

LLM_PROVIDER=mock


This means the extraction pipeline works without an API key. OpenAI / Anthropic adapters can be connected later through the provider interface.

## 9. Demo flow

1. Open Overview.
2. Open Inbox and run the extraction studio with a Hinglish message.
3. Inspect extracted intent/product/language/confidence.
4. Open Orders and Finance.
5. Generate an invoice PDF from the API.
6. Open Follow-ups to show AI-generated reminders.
7. Ask a natural-language question in Ask Nexora.
8. Open Evaluation Lab and explain the three evaluation dimensions.

## 10. Research contribution

Nexora does not evaluate an LLM only on extraction accuracy. It evaluates the complete user-facing analytical system across:

- field precision / recall / F1
- exact match
- JSON validity
- schema pass rate
- hallucination rate
- latency / token cost
- robustness to typos and Hinglish
- chart-type correctness
- query-spec accuracy
- insight faithfulness
- task completion
- time-to-task
- manual corrections
- trust / clarity
- SUS usability score

## 11. ER diagram

erDiagram
CUSTOMER ||--o{ CONVERSATION : has
CONVERSATION ||--o{ MESSAGE : contains
CONVERSATION ||--o{ EXTRACTION : produces
CUSTOMER ||--o{ ORDER : places
ORDER ||--o{ ORDER_ITEM : contains
PRODUCT ||--o{ ORDER_ITEM : sold_as
ORDER ||--o{ PAYMENT : receives
ORDER ||--o| INVOICE : billed_by
ORDER ||--o{ PAYMENT_LINK : has
CUSTOMER ||--o{ FOLLOWUP : needs
EVALUATION_RUN ||--o{ EVALUATION_RESULT : records
USER ||--o{ AUDIT_LOG : creates


## 12. Security / production notes

Payment and social-channel integrations are simulations/stubs. Before production: use PostgreSQL, HTTPS, managed secrets, real OAuth/JWT identity management, provider-specific webhook verification, CSRF/CORS controls, rate limiting at the edge and a compliant payment gateway.

## 13. License / academic use

Intended as an academic / portfolio demonstration and extensible product prototype.

## Live dashboard integration

The dashboard is connected to the FastAPI data layer rather than relying on the original illustrative KPI values. Overview KPIs, revenue series, channel mix, customers, orders, invoices, payments, follow-ups and evaluation results are loaded from API endpoints. The Inbox simulator writes a real conversation through the extraction pipeline and refreshes the conversation list.

### Reset demo data

From backend/, run python reset_demo.py whenever you want a clean demo dataset. This regenerates 30 conversations, conversation-derived orders, sample invoices/payments and follow-ups.

## 14. NEXORA 2.1 product polish

The current build includes a production-style extraction studio rather than a generic result card. Each extraction displays:

- intent, product, sentiment and language
- per-field confidence and source-message evidence
- schema validation state
- a five-stage live pipeline: Ingest → Extract → Validate → CRM → Action
- created order reference and amount when an order is generated
- scheduled follow-up details when detected
- explicit MockLLM offline/privacy status

The overview, analytics, orders, finance and follow-up views read from the same API/database, so actions taken in Inbox can change the workspace metrics.

### Demo credentials

The development API can bootstrap the demo administrator on the first login request:

username: admin
password: nexora123


Change this immediately for any non-demo deployment and replace the development SECRET_KEY.

### Final verification

The packaged backend has been syntax-checked and the automated test suite passes. The local frontend was previously verified with Vite; the package intentionally does not contain node_modules, so run npm install locally before starting it.

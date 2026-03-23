# MapInsights — Project Brief for Claude Code

## **Project Overview**

**MapInsights** is an AI-powered SaaS tool that provides business owners (shops, restaurants, cafés) with detailed feedback on their Google Maps presence. Users pay a one-time fee, share their Google Maps link, and receive:

1. **Overall Score** with breakdowns across three dimensions:
   - Media quality (photos, videos)
   - Information availability (contact, website, hours)
   - Review sentiment & patterns

2. **Detailed Feedback** on each dimension with actionable insights
3. **Actionable Recommendations** to improve their Google Maps presence

---

## **Core Value Proposition**

- **Problem**: Local business owners lack visibility into how their Maps listing performs and what's missing
- **Solution**: One-click analysis powered by AI, providing structured feedback in ~2 minutes
- **Revenue Model**: One-time payment (~$5–$15 per analysis) to cover API costs + margin
- **Target Users**: Solo entrepreneurs, small business owners, marketing agencies managing local businesses

---

## **Technical Stack**

### **Backend**
- **Framework**: FastAPI (async, type-safe, auto-docs)
- **Package Manager**: UV (fast, deterministic Python dependency management)
- **Web Server**: Uvicorn (ASGI, async-first)
- **Data Extraction**: Apify API (Google Maps scraper actor)
- **AI Processing**: LangChain + Claude API (concept disentanglement, structured analysis)
- **Payments**: Stripe API (one-time charges, webhook handling)
- **Database**: (TBD: PostgreSQL recommended for production)
- **Logging**: Loguru (structured, async-friendly)
- **Testing**: Pytest + pytest-asyncio

### **Frontend**
- **Framework**: Next.js (file-based routing, serverless API routes)
- **Language**: TypeScript
- **UI**: React + Tailwind CSS
- **Deployment**: Vercel (integrated with Next.js, automatic CI/CD)
- **Payments**: Stripe.js client library
- **HTTP Client**: Axios or Fetch API

### **Infrastructure**
- **Deployment**: Vercel (frontend + serverless functions) + Railway/Render (FastAPI backend)
- **Environment Management**: `.env` files for secrets
- **Version Control**: Git + GitHub

---

## **Data Flow Architecture**

```
User Input (Google Maps URL)
    ↓
Frontend Form (MapInputForm.tsx)
    ↓
Stripe Payment Processing
    ↓
FastAPI /analyze endpoint
    ↓
Apify Scraper (Google Maps data extraction)
    ↓
LangChain Analysis Chains
    ├─ Media Chain (photo/video quality)
    ├─ Info Chain (contact/website completeness)
    └─ Review Chain (sentiment analysis, pattern detection)
    ↓
Structured Feedback Object
    ↓
Frontend Results Display (ScoreCard, MediaFeedback, etc.)
```

---

## Project Folder Structure

This document outlines the recommended folder structure for MapInsights, designed for clarity, modularity, and Claude Code compatibility (direct file edits + terminal workflows).

---

## **Root Structure**

```
app/
├── backend/                    # FastAPI backend
├── frontend/                   # Next.js/React frontend (Vercel deployment)
├── scripts/                    # Utility scripts (db migrations, setup, etc.)
├── docs/                       # Documentation
├── .env                        # Environment variables template
├── .gitignore
├── README.md
└── docker-compose.yml          # Local dev environment
```

---

## **Backend Structure** (`backend/`)

See `backend/CLAUDE.md`.

---

## **Frontend Structure** (`frontend/`)

See `frontend/CLAUDE.md`. 

---

## **Scripts Structure** (`scripts/`)

```
scripts/
├── setup.sh                    # Initial project setup
├── dev.sh                      # Local development startup
├── seed_db.py                  # Database seeding (if applicable)
├── test_apify.py               # Manual Apify testing script
└── deploy.sh                   # Deployment automation
```

---

## **Documentation Structure** (`docs/`)

```
docs/
├── API.md                      # API endpoint documentation
├── ARCHITECTURE.md             # System design & data flow
├── SETUP.md                    # Development setup guide
├── DEPLOYMENT.md               # Production deployment guide
├── TASK_CHECKLIST.md           # Task progress tracker
└── DECISIONS.md                # ADRs (Architecture Decision Records)
```

---

## **Key Design Principles**

1. **Separation of Concerns**: Routes → Services → Chains/Models
2. **Testability**: Each service has isolated unit tests; mocks in `fixtures/`
3. **Claude Code Compatible**: Flat file edits (`app/routes/scraper.py`, `app/services/apify_service.py`) align with direct terminal workflows
4. **Scalability**: Chains, services, and routes are independently extendable
5. **Documentation**: Each folder has a README or inline docstrings explaining purpose

---
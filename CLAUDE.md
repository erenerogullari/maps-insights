# MapInsights — Project Folder Structure

This document outlines the recommended folder structure for MapInsights, designed for clarity, modularity, and Claude Code compatibility (direct file edits + terminal workflows).

---

## **Root Structure**

```
app/
├── backend/                    # FastAPI backend
├── frontend/                   # Next.js/React frontend (Vercel deployment)
├── scripts/                    # Utility scripts (db migrations, setup, etc.)
├── tests/                      # Test suite
├── docs/                       # Documentation
├── .env                        # Environment variables template
├── .gitignore
├── README.md
└── docker-compose.yml          # Local dev environment
```

---

## **Backend Structure** (`backend/`)

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Settings (env vars, constants)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── scraper.py          # Task 1.3: Apify scraper endpoints
│   │   ├── analysis.py         # Task 2.x: LangChain analysis endpoints
│   │   ├── payment.py          # Task 3.x: Stripe payment endpoints
│   │   └── health.py           # Health check / status endpoints
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── apify_service.py    # Apify API interactions
│   │   ├── langchain_service.py # LangChain chain orchestration
│   │   ├── stripe_service.py   # Stripe API interactions
│   │   └── storage_service.py  # Data persistence (DB/file ops)
│   ├── models/                 # Pydantic models (request/response schemas)
│   │   ├── __init__.py
│   │   ├── scraper.py          # e.g., GoogleMapsUrlInput, ScraperResponse
│   │   ├── analysis.py         # e.g., FeedbackResponse, ScoreCard
│   │   └── payment.py          # e.g., PaymentRequest, PaymentStatus
│   ├── chains/                 # LangChain chains (Category 2)
│   │   ├── __init__.py
│   │   ├── feedback_chain.py   # Main analysis chain
│   │   ├── media_chain.py      # Media-specific analysis
│   │   ├── info_chain.py       # Information availability analysis
│   │   └── review_chain.py     # Review sentiment/analysis chain
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── validators.py       # URL validation, input sanitization
│   │   ├── rate_limit.py       # Rate limiting logic
│   │   ├── logger.py           # Logging configuration
│   │   └── decorators.py       # Reusable decorators (auth, timing, etc.)
│   ├── middleware/             # FastAPI middleware
│   │   ├── __init__.py
│   │   ├── auth.py             # Payment verification middleware
│   │   └── error_handler.py    # Global error handling
│   └── db/                     # Database (if using)
│       ├── __init__.py
│       ├── models.py           # SQLAlchemy/ORM models
│       ├── session.py          # DB connection management
│       └── schemas.py          # Pydantic schemas for DB operations
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── test_routes/
│   │   ├── test_scraper.py
│   │   ├── test_analysis.py
│   │   └── test_payment.py
│   ├── test_services/
│   │   ├── test_apify_service.py
│   │   ├── test_langchain_service.py
│   │   └── test_stripe_service.py
│   └── fixtures/
│       ├── mock_apify_response.json
│       └── mock_google_maps_data.json
├── requirements.txt            # Python dependencies
├── requirements-dev.txt        # Dev dependencies (pytest, black, etc.)
├── Dockerfile                  # Container image
└── .env                        # Backend-specific env vars
```

---

## **Frontend Structure** (`frontend/`)

```
frontend/
├── public/                     # Static assets
│   ├── favicon.ico
│   └── images/
├── src/
│   ├── pages/                  # Next.js pages (file-based routing)
│   │   ├── index.tsx           # Landing page
│   │   ├── dashboard.tsx       # Main analysis page
│   │   ├── pricing.tsx         # Pricing/payment page
│   │   ├── results/[id].tsx    # Analysis result detail page
│   │   └── api/                # API routes (Next.js serverless)
│   │       ├── webhook/stripe.ts  # Stripe webhook handler
│   │       └── health.ts          # Health check
│   ├── components/             # React components
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   ├── forms/
│   │   │   └── MapInputForm.tsx    # URL input form
│   │   ├── results/
│   │   │   ├── ScoreCard.tsx       # Overall score display
│   │   │   ├── MediaFeedback.tsx
│   │   │   ├── InfoFeedback.tsx
│   │   │   └── ReviewFeedback.tsx
│   │   └── shared/
│   │       ├── LoadingSpinner.tsx
│   │       └── ErrorBoundary.tsx
│   ├── hooks/                  # Custom React hooks
│   │   ├── useAnalysis.ts      # Hook for calling analysis API
│   │   └── usePayment.ts       # Hook for Stripe payment
│   ├── lib/                    # Utility functions
│   │   ├── api.ts              # API client (axios/fetch)
│   │   ├── stripe.ts           # Stripe client initialization
│   │   └── validators.ts       # Frontend validation
│   ├── styles/                 # Global styles (CSS/Tailwind)
│   │   └── globals.css
│   ├── types/                  # TypeScript types
│   │   ├── analysis.ts
│   │   ├── payment.ts
│   │   └── api.ts
│   └── App.tsx (or _app.tsx)   # Root component
├── next.config.js              # Next.js configuration
├── tsconfig.json               # TypeScript config
├── tailwind.config.js          # Tailwind CSS config (if using)
├── package.json
├── .env.local.example          # Frontend env vars template
└── .vercelignore
```

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

## **Tests Structure** (`tests/`)

```
tests/
├── integration/
│   ├── test_scraper_to_analysis.py   # End-to-end flow
│   └── test_payment_flow.py          # Payment → analysis flow
├── unit/
│   ├── test_validators.py
│   ├── test_rate_limiting.py
│   └── test_chain_logic.py
└── fixtures/
    ├── apify_responses/
    ├── google_maps_samples/
    └── stripe_mocks/
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

## **Environment Variables Layout**

**Backend** (`backend/.env`):
```
# Apify
APIFY_API_KEY=xxx
APIFY_ACTOR_ID=xxx

# LangChain
OPENAI_API_KEY=xxx  # or other LLM provider
LANGCHAIN_DEBUG=false

# Stripe
STRIPE_SECRET_KEY=xxx
STRIPE_PUBLISHABLE_KEY=xxx

# Database (if applicable)
DATABASE_URL=postgresql://user:pass@localhost/mapinsights

# General
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**Frontend** (`.env.local`):
```
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=xxx
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

## **Key Design Principles**

1. **Separation of Concerns**: Routes → Services → Chains/Models
2. **Testability**: Each service has isolated unit tests; mocks in `fixtures/`
3. **Claude Code Compatible**: Flat file edits (`app/routes/scraper.py`, `app/services/apify_service.py`) align with direct terminal workflows
4. **Scalability**: Chains, services, and routes are independently extendable
5. **Documentation**: Each folder has a README or inline docstrings explaining purpose

---

## **Quick Navigation Reference**

| **Task Category** | **Primary Folders** |
|---|---|
| **Task 1.x (Apify)** | `backend/app/routes/scraper.py`, `backend/app/services/apify_service.py`, `backend/app/models/scraper.py` |
| **Task 2.x (LangChain)** | `backend/app/chains/`, `backend/app/services/langchain_service.py`, `backend/app/models/analysis.py` |
| **Task 3.x (Stripe)** | `backend/app/routes/payment.py`, `backend/app/services/stripe_service.py`, `frontend/src/hooks/usePayment.ts` |
| **Testing** | `tests/`, `backend/tests/` |
| **Frontend** | `frontend/src/` (components, pages, hooks) |

---
# MapInsights Backend — Claude Code Context

## **Project Overview (Backend Focus)**

MapInsights is an AI-powered SaaS tool for local business owners to get detailed feedback on their Google Maps presence. This document covers **backend architecture only** — the FastAPI application that orchestrates data extraction, AI analysis, and payment processing.

---

## **Backend Technology Stack**

- **Framework**: FastAPI (async, type-safe, auto-API docs)
- **Package Manager**: UV (fast, deterministic dependency management)
- **Web Server**: Uvicorn (ASGI server, async-first)
- **Data Extraction**: Apify API (Google Maps scraper)
- **AI Processing**: LangChain + Claude API (structured analysis)
- **Payments**: Stripe API (webhooks, idempotency)
- **Database**: PostgreSQL (recommended, not yet integrated)
- **Logging**: Loguru (structured, async-friendly)
- **Testing**: Pytest + pytest-asyncio
- **Code Quality**: Ruff (linting), Black (formatting), Mypy (type checking)

---

## **Backend Architecture**

### **Data Flow**

```
HTTP Request (Google Maps URL)
    ↓
FastAPI Route (/analyze, /payment, /scraper)
    ↓
Service Layer (apify_service, langchain_service, stripe_service)
    ↓
External APIs (Apify, LLM, Stripe)
    ↓
Response (JSON)
    ↓
HTTP Response → Frontend
```

### **Folder Structure**

```
backend/
├── app/
│   ├── main.py                 # FastAPI app init, route registration
│   ├── config.py               # Settings, env vars, constants
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── scraper.py          # Task 1: Apify scraper endpoints
│   │   ├── analysis.py         # Task 2: LangChain analysis endpoints
│   │   ├── payment.py          # Task 3: Stripe payment endpoints
│   │   └── health.py           # Health check endpoint
│   ├── services/
│   │   ├── __init__.py
│   │   ├── apify_service.py    # Apify API client, job polling
│   │   ├── langchain_service.py # Chain orchestration, LLM calls
│   │   ├── stripe_service.py   # Stripe API, webhook verification
│   │   └── storage_service.py  # Data persistence (if using DB)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── scraper.py          # GoogleMapsUrlInput, ScraperResponse
│   │   ├── analysis.py         # FeedbackResponse, ScoreCard
│   │   └── payment.py          # PaymentRequest, PaymentStatus
│   ├── chains/                 # LangChain chains (Task 2)
│   │   ├── __init__.py
│   │   ├── feedback_chain.py   # Main orchestration chain
│   │   ├── media_chain.py      # Photo/video analysis
│   │   ├── info_chain.py       # Info completeness check
│   │   └── review_chain.py     # Review sentiment & patterns
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── validators.py       # URL validation, input sanitization
│   │   ├── rate_limit.py       # In-memory rate limiting
│   │   ├── logger.py           # Loguru configuration
│   │   └── decorators.py       # Reusable decorators (timing, logging)
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py             # Token/API key verification
│   │   └── error_handler.py    # Global exception handling
│   └── db/                     # Database layer (future)
│       ├── __init__.py
│       ├── models.py           # SQLAlchemy ORM models
│       ├── session.py          # DB connection pool
│       └── schemas.py          # Pydantic schemas for DB
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures, mocks
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
├── pyproject.toml              # UV dependencies, project metadata
├── uv.lock                     # Lock file (commit to version control)
├── .env.example                # Env vars template
├── .gitignore                  # Python-specific ignores
├── Dockerfile                  # Container image (deployment)
└── README.md                   # Backend setup & API docs
```

---

## **Environment Variables (Backend)**

**File**: `backend/.env`

```
# Apify Configuration
APIFY_API_KEY=your_api_key_here
APIFY_ACTOR_ID=apify/google-maps-scraper
APIFY_TIMEOUT_SECONDS=300

# LLM / LangChain Configuration
ANTHROPIC_API_KEY=your_api_key_here
LLM_MODEL=claude-3-5-sonnet-20241022
LANGCHAIN_DEBUG=false

# Stripe Configuration
STRIPE_SECRET_KEY=sk_live_or_sk_test_key_here
STRIPE_PUBLISHABLE_KEY=pk_live_or_pk_test_key_here
STRIPE_WEBHOOK_SECRET=whsec_xxxx_here
STRIPE_PRICE_ID=price_xxxx_here

# Database (if using)
DATABASE_URL=postgresql://user:password@localhost:5432/mapinsights

# General Configuration
ENVIRONMENT=development  # or production
LOG_LEVEL=INFO           # DEBUG, INFO, WARNING, ERROR
CORS_ORIGINS=["http://localhost:3000", "https://mapinsights.com"]
```

---

## **Task Categories (Backend)**

### **Task 1: Web Scraping & Data Extraction (Apify)**

**Objective**: Build endpoint to scrape Google Maps data via Apify API.

**Files to create/modify**:
- `app/routes/scraper.py` — POST `/scrape` endpoint
- `app/services/apify_service.py` — Apify client logic
- `app/models/scraper.py` — Request/response schemas
- `app/utils/validators.py` — URL validation

**Subtasks**:
- 1.1: Research Apify Google Maps actor & field mapping
- 1.2: Set up Apify account, test scraper manually
- 1.3: Implement FastAPI endpoint + async job polling
- 1.4: Add validation, rate limiting, logging

**Expected Output**: Structured JSON from Google Maps (title, rating, photos, reviews, contact, hours, etc.)

---

### **Task 2: LangChain & AI Feedback Generation**

**Objective**: Process scraped data through LLM chains to generate structured feedback.

**Files to create**:
- `app/chains/feedback_chain.py` — Main orchestration chain
- `app/chains/media_chain.py` — Photo/video quality analysis
- `app/chains/info_chain.py` — Information completeness check
- `app/chains/review_chain.py` — Review sentiment & pattern detection
- `app/services/langchain_service.py` — Chain execution & prompt management
- `app/routes/analysis.py` — POST `/analyze` endpoint

**Subtasks** (defined later):
- 2.1: Design prompt templates for each chain
- 2.2: Implement media analysis chain
- 2.3: Implement info availability chain
- 2.4: Implement review analysis chain
- 2.5: Integrate chains with Apify data

**Expected Output**: Structured feedback object with scores and recommendations

---

### **Task 3: Payment Processing & Auth**

**Objective**: Integrate Stripe for one-time payments and protect endpoints.

**Files to create**:
- `app/routes/payment.py` — POST `/checkout`, POST `/webhook/stripe`
- `app/services/stripe_service.py` — Stripe API client
- `app/middleware/auth.py` — Payment verification middleware

**Subtasks** (defined later):
- 3.1: Create Stripe checkout session endpoint
- 3.2: Implement webhook signature verification
- 3.3: Add payment status tracking
- 3.4: Protect analysis endpoints with auth

**Expected Output**: Payment processing flow + protected endpoints

---

## **Key Design Patterns**

### **1. Service Layer Pattern**
Routes delegate to services; services handle external API calls and business logic.

```python
# routes/scraper.py
@router.post("/scrape")
async def scrape(url: GoogleMapsUrl) -> ScraperResponse:
    result = await apify_service.scrape_maps(url.url)
    return ScraperResponse(**result)

# services/apify_service.py
async def scrape_maps(url: str) -> dict:
    # Apify API logic here
    pass
```

### **2. Async/Await for I/O**
All external API calls are async to avoid blocking.

```python
async def wait_for_job(job_id: str) -> dict:
    while True:
        status = await httpx.get(f"https://api.apify.com/v2/acts/{actor_id}/runs/{job_id}")
        if status.json()["status"] == "SUCCEEDED":
            return status.json()
        await asyncio.sleep(2)
```

### **3. Pydantic Models for Type Safety**
All inputs/outputs validated and type-hinted.

```python
class GoogleMapsUrl(BaseModel):
    url: HttpUrl
    
class ScoreCard(BaseModel):
    media_score: float
    info_score: float
    review_score: float
    overall_score: float
```

### **4. Environment-Based Configuration**
Settings loaded from `.env`, with defaults in `config.py`.

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    apify_api_key: str
    stripe_secret_key: str
    environment: str = "development"
    
    class Config:
        env_file = ".env"
```

---

## **Development Workflow**

### **Setup**
```bash
cd backend
uv sync  # Install dependencies from lock file
```

### **Run Locally**
```bash
uv run uvicorn app.main:app --reload
# Server on http://localhost:8000
# Docs on http://localhost:8000/docs
```

### **Run Tests**
```bash
uv run pytest tests/ -v
uv run pytest tests/test_routes/test_scraper.py  # Single file
uv run pytest tests/ --cov=app               # With coverage
```

### **Code Quality**
```bash
uv run ruff check app/          # Linting
uv run black app/               # Formatting
uv run mypy app/                # Type checking
```

### **Environment**
- Copy `.env.example` to `.env`
- Fill in API keys (Apify, Stripe, Anthropic)
- Never commit `.env` to version control

---

## **API Endpoints (Overview)**

### **Health Check**
```
GET /health
Response: {"status": "ok"}
```

### **Scraper (Task 1)**
```
POST /scrape
Body: {"url": "https://maps.google.com/..."}
Response: {
  "status": "completed",
  "data": {
    "title": "...",
    "rating": 4.5,
    "photos": [...],
    "reviews": [...]
  }
}
```

### **Analysis (Task 2)**
```
POST /analyze
Body: {"google_maps_data": {...}}
Response: {
  "overall_score": 78,
  "media": {...},
  "info": {...},
  "reviews": {...}
}
```

### **Payment (Task 3)**
```
POST /checkout
Body: {"email": "user@example.com"}
Response: {"session_id": "cs_xxxx", "url": "https://checkout.stripe.com/..."}

POST /webhook/stripe
Body: Stripe webhook event
Response: 200 OK
```

---

## **Testing Strategy**

- **Unit tests**: Mock external APIs (Apify, Stripe, LLM)
- **Integration tests**: Full flow with real/mock data
- **Fixtures**: Store mock responses in `tests/fixtures/`

**Example**:
```python
# tests/test_services/test_apify_service.py
@pytest.mark.asyncio
async def test_scrape_maps():
    with open("fixtures/mock_apify_response.json") as f:
        mock_data = json.load(f)
    
    result = await apify_service.scrape_maps("https://...")
    assert result["title"] == mock_data["title"]
```

---

## **Deployment**

### **Local Docker**
```bash
docker build -t mapinsights-backend .
docker run -p 8000:8000 --env-file .env mapinsights-backend
```

### **Production (Railway/Render)**
- Push to GitHub
- Set env vars in hosting provider
- Deploy Docker image or connect to repo for auto-deploy

---

## **Current Status**

🔄 **Phase**: Task 1 — Apify Integration

- [x] UV initialized in `backend/`
- [x] Dependencies installed
- [ ] `config.py` created
- [ ] `app/main.py` initialized
- [ ] Task 1.1–1.4 in progress

**Next**: Complete Task 1 setup before LangChain integration.

---

## **References**

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Apify API Reference](https://apify.com/docs/api/v2)
- [LangChain Python](https://python.langchain.com/)
- [Stripe API](https://stripe.com/docs/api)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [Loguru](https://loguru.readthedocs.io/)
- [UV Docs](https://docs.astral.sh/uv/)
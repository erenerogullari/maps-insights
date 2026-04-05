# MapInsights Backend — Task Tracker

## Current Status

**Phase**: Task 1 — Apify Integration

- [x] UV initialized in `backend/`
- [x] Dependencies installed
- [x] `config.py` created
- [x] `app/main.py` initialized
- [x] Task 1.1
- [x] Task 1.2
- [x] Task 1.3
- [ ] Task 1.4

---

## Task 1: Web Scraping & Data Extraction (Apify)

**Objective**: Build endpoint to scrape Google Maps data via Apify API.

**Expected Output**: Structured JSON from Google Maps (title, rating, photos, reviews, contact, hours, etc.)

**Files to create/modify**:
- `app/models/scraper.py` — Request/response schemas
- `app/utils/url_utils.py` — URL validation
- `app/services/apify_service.py` — Apify client logic
- `app/routes/scraper.py` — POST `/scrape` endpoint

### Subtask 1.1 — Pydantic models (`app/models/scraper.py`)
- [x] Define `ScraperInput` with URL and `include_photos` fields (user-selectable); `max_reviews` handled globally in config
- [x] Define `ScraperResponse` with structured fields: `title`, `rating`, `photos`, `reviews`, `contact`, `hours`, `address`, `website`, `total_reviews`
- [x] Add `__init__.py` to `app/models/`

### Subtask 1.2 — URL validator (`app/utils/url_utils.py`)
- [x] Validate Google Maps URL format (handle `maps.google.com`, `goo.gl/maps`, `maps.app.goo.gl` variants)
- [x] Sanitize input before passing to Apify
- [x] Raise `ValueError` with a clear message on invalid URLs
- [x] Add `__init__.py` to `app/utils/`

### Subtask 1.3 — Apify service (`app/services/apify_service.py`)
- [x] Async Apify client using `httpx`
- [x] Trigger scraper actor with the Maps URL
- [x] Poll job status until `SUCCEEDED` or configurable timeout (default 300s)
- [x] Parse and return structured dataset results
- [x] Raise descriptive exceptions on failure/timeout
- [x] Add `__init__.py` to `app/services/`

### Subtask 1.4 — Scraper route + wire into `main.py`
- [ ] `POST /scrape` endpoint in `app/routes/scraper.py`
- [ ] Delegate to `apify_service.scrape_maps()`
- [ ] Return `ScraperResponse`
- [ ] Add Loguru logging (request in, job start, job complete, errors)
- [ ] Register router in `app/main.py`
- [ ] Add `__init__.py` to `app/routes/`

---

## Task 2: LangChain & AI Feedback Generation

**Objective**: Process scraped data through LLM chains to generate structured feedback.

**Expected Output**: Structured feedback object with scores and recommendations

**Files to create**:
- `app/chains/feedback_chain.py` — Main orchestration chain
- `app/chains/media_chain.py` — Photo/video quality analysis
- `app/chains/info_chain.py` — Information completeness check
- `app/chains/review_chain.py` — Review sentiment & pattern detection
- `app/services/langchain_service.py` — Chain execution & prompt management
- `app/routes/analysis.py` — POST `/analyze` endpoint

### Subtasks
- [ ] 2.1: Design prompt templates for each chain
- [ ] 2.2: Implement media analysis chain
- [ ] 2.3: Implement info availability chain
- [ ] 2.4: Implement review analysis chain
- [ ] 2.5: Integrate chains with Apify data

---

## Task 3: Payment Processing & Auth

**Objective**: Integrate Stripe for one-time payments and protect endpoints.

**Expected Output**: Payment processing flow + protected endpoints

**Files to create**:
- `app/routes/payment.py` — POST `/checkout`, POST `/webhook/stripe`
- `app/services/stripe_service.py` — Stripe API client
- `app/middleware/auth.py` — Payment verification middleware

### Subtasks
- [ ] 3.1: Create Stripe checkout session endpoint
- [ ] 3.2: Implement webhook signature verification
- [ ] 3.3: Add payment status tracking
- [ ] 3.4: Protect analysis endpoints with auth

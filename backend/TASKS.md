# MapInsights Backend — Task Tracker

## Current Status

**Phase**: Task 2 — LangChain & AI Feedback Generation

- [x] Task 2.1 — Install LangChain dependencies
- [x] Task 2.2 — Pydantic output models (`app/models/analysis.py`)
- [x] Task 2.3 — Media chain
- [ ] Task 2.4 — Info chain
- [ ] Task 2.5 — Review chain
- [ ] Task 2.6 — Feedback orchestration chain
- [ ] Task 2.7 — LangChain service
- [ ] Task 2.8 — Analysis route + wire into `main.py`

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
- [x] `POST /scrape` endpoint in `app/routes/scraper.py`
- [x] Delegate to `apify_service.scrape_maps()`
- [x] Return `ScraperResponse`
- [x] Add Loguru logging (job start, job complete, errors)
- [x] Register router in `app/main.py`
- [x] Add `__init__.py` to `app/routes/`

---

## Task 2: LangChain & AI Feedback Generation

**Objective**: Process scraped `ScraperResponse` data through three parallel LLM chains (media, info, reviews), then aggregate into a single structured `FeedbackResponse` with scores and recommendations.

**Expected Output**: `FeedbackResponse` with `overall_score`, per-dimension scores (0–100), LLM-generated feedback text, and actionable recommendations per dimension.

**LLM**: `ChatGoogleGenerativeAI` (`gemini-2.0-flash`) via `langchain-google-genai`. Use `with_structured_output()` on every chain so the LLM returns typed Pydantic objects directly — no manual JSON parsing.

**Files to create/modify**:
- `pyproject.toml` — add LangChain dependencies
- `app/models/analysis.py` — output Pydantic models
- `app/chains/__init__.py`
- `app/chains/media_chain.py` — photo quality scoring chain
- `app/chains/info_chain.py` — information completeness scoring chain
- `app/chains/review_chain.py` — review sentiment & pattern scoring chain
- `app/chains/feedback_chain.py` — orchestrator: runs all three concurrently, computes overall score
- `app/services/langchain_service.py` — initializes LLM, exposes `analyze()` entry point
- `app/routes/analysis.py` — `POST /analyze` endpoint
- `app/main.py` — register analysis router

---

### Subtask 2.1 — Install LangChain dependencies (`pyproject.toml`)

Add to `[project] dependencies`:
- `langchain>=0.3`
- `langchain-core>=0.3`
- `langchain-google-genai>=2.0`

Run `uv sync` after updating.

---

### Subtask 2.2 — Pydantic output models (`app/models/analysis.py`)

Define the following models. All score fields are `int` in range `0–100`.

```python
class MediaFeedback(BaseModel):
    score: int                          # 0–100
    photo_count: int                    # number of photos found
    feedback: str                       # LLM-generated paragraph
    recommendations: list[str]          # 2–4 concrete action items

class InfoFeedback(BaseModel):
    score: int                          # 0–100
    fields_present: list[str]           # e.g. ["phone", "website", "address", "hours"]
    fields_missing: list[str]           # fields that are None/empty
    feedback: str                       # LLM-generated paragraph
    recommendations: list[str]          # 2–4 concrete action items

class ReviewFeedback(BaseModel):
    score: int                          # 0–100
    sentiment: Literal["positive", "mixed", "negative"]
    key_themes: list[str]               # recurring topics found in reviews
    owner_response_present: bool        # whether any owner replies were detected
    feedback: str                       # LLM-generated paragraph
    recommendations: list[str]          # 2–4 concrete action items

class FeedbackResponse(BaseModel):
    business_name: str | None
    overall_score: int                  # weighted average: media 25%, info 35%, reviews 40%
    media: MediaFeedback
    info: InfoFeedback
    reviews: ReviewFeedback
    summary: str                        # 2–3 sentence executive summary
    generated_at: datetime
```

Add `analysis.py` export to `app/models/__init__.py`.

---

### Subtask 2.3 — Media chain (`app/chains/media_chain.py`)

**Input**: `photos: list[PhotoItem] | None`, `title: str | None` (extracted from `ScraperResponse`)

**Logic**:
1. Compute `photo_count = len(photos) if photos else 0`
2. Build a prompt that gives the LLM: the business name, the photo count, and all available photo descriptions. Ask it to score the media presence (0–100) using these guidelines embedded in the prompt:
   - 0 photos → max score ~10 ("No photos — critical gap")
   - 1–4 → max ~40
   - 5–9 → max ~60
   - 10–19 → max ~80
   - 20+ → up to 100 (penalise if all descriptions look identical/generic)
3. Use `llm.with_structured_output(MediaFeedback)` so the chain returns a typed `MediaFeedback` directly.
4. The `recommendations` list must always have at least one item even if the score is high.

**Expose**: `async def run_media_chain(llm, photos, title) -> MediaFeedback`

---

### Subtask 2.4 — Info chain (`app/chains/info_chain.py`)

**Input**: `phone_number`, `website`, `address`, `hours`, `total_reviews`, `rating` (extracted from `ScraperResponse`)

**Logic**:
1. Pre-compute `fields_present` / `fields_missing` deterministically (no LLM needed for detection):
   - Tracked fields: `phone`, `website`, `address`, `hours`
   - A field is "present" if it's non-None and non-empty. For `hours`, it must be a dict with ≥ 1 entry.
2. Build base score from field presence: each field = 20 pts (max 80 from data completeness alone). The remaining 20 pts come from LLM judgement (e.g. hours covering all 7 days, website appears functional, phone looks valid).
3. Pass `fields_present`, `fields_missing`, and raw field values to the LLM prompt.
4. Use `llm.with_structured_output(InfoFeedback)`. The LLM fills `score` (must be within 5 pts of the deterministic base), `feedback`, and `recommendations`.

**Expose**: `async def run_info_chain(llm, scraper_data: ScraperResponse) -> InfoFeedback`

---

### Subtask 2.5 — Review chain (`app/chains/review_chain.py`)

**Input**: `reviews: list[ReviewItem] | None`, `total_reviews: int | None`, `rating: float | None`

**Logic**:
1. Pre-compute deterministic signals before calling the LLM:
   - `rating_pts` (0–40): ≥4.5→40, ≥4.0→30, ≥3.5→20, ≥3.0→10, <3.0→0, None→0
   - `volume_pts` (0–30): ≥100→30, ≥50→20, ≥20→10, ≥5→5, <5→0, None→0
   - The LLM assigns the remaining 0–30 pts based on review text quality, theme variety, and whether owner responses are detected.
2. Pass to the LLM: the rating, total_reviews count, and the text of the first `N` reviews (cap at 20 to stay within context — use `settings.scraper_max_reviews` as the source cap). Instruct the LLM to identify `key_themes`, assign `sentiment`, detect `owner_response_present`, and return `score` (full 0–100, but it must reconcile with the pre-computed floor of `rating_pts + volume_pts`).
3. Use `llm.with_structured_output(ReviewFeedback)`.

**Expose**: `async def run_review_chain(llm, reviews, total_reviews, rating) -> ReviewFeedback`

---

### Subtask 2.6 — Feedback orchestration chain (`app/chains/feedback_chain.py`)

**Logic**:
1. Accept `ScraperResponse` and a pre-initialised `llm` instance.
2. Run all three chains concurrently: `await asyncio.gather(run_media_chain(...), run_info_chain(...), run_review_chain(...))`.
3. Compute `overall_score = round(media.score * 0.25 + info.score * 0.35 + reviews.score * 0.40)`.
4. Make a final LLM call to generate `summary` (2–3 sentences describing the business's overall Maps presence) — pass the three sub-scores and the business name. This call does NOT use `with_structured_output`; just extract the string from the response.
5. Return a fully populated `FeedbackResponse` with `generated_at=datetime.utcnow()`.

**Expose**: `async def run_feedback_chain(scraper_data: ScraperResponse, llm) -> FeedbackResponse`

---

### Subtask 2.7 — LangChain service (`app/services/langchain_service.py`)

**Logic**:
1. On import, initialise `ChatGoogleGenerativeAI(model=settings.llm_model, google_api_key=settings.google_api_key)` once (module-level singleton, not per-request).
2. Expose a single async function: `async def analyze(data: ScraperResponse) -> FeedbackResponse`.
3. Delegate entirely to `run_feedback_chain(data, llm)` from the orchestration chain.
4. Wrap the call in a `try/except` — catch `Exception`, log with `logger.error(f"LangChain analysis failed: {e}")`, and re-raise as `RuntimeError("Analysis failed")` so the route can return a clean 500.
5. Log at INFO level: analysis start (business name), each chain completion with its score, and total elapsed time.

---

### Subtask 2.8 — Analysis route + wire into `main.py` (`app/routes/analysis.py`)

- `POST /analyze` — accepts `ScraperResponse` as the request body (field alias `google_maps_data` is NOT needed — use the model directly as body since this is an internal API)
- Delegate to `langchain_service.analyze(body)`
- Return `FeedbackResponse`
- Log at INFO: `"Analysis requested for business={body.title}"`
- On `RuntimeError` from the service, return HTTP 500 with `{"detail": "Analysis failed, please try again"}`
- Register the router with prefix `""` and tag `"analysis"` in `app/main.py`
- Add `app/chains/__init__.py` (empty)

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

---
name: MapInsights current project phase
description: Current development phase and what has been built so far in the backend
type: project
---

Project is in Task 1 (Apify Integration), actively progressing on branch `backend/web-scraper`.

Completed so far:
- UV initialized, dependencies installed
- `config.py` with pydantic-settings
- `app/main.py` initialized
- `app/models/scraper.py` — Pydantic models (`ScraperInput`, `ScraperResponse`, `ReviewItem`, `PhotoItem`); `max_reviews` removed from `ScraperInput` — moved to global config
- `app/models/__init__.py` added
- `app/utils/url_utils.py` — `sanitize_maps_url()` strips non-essential query params, keeps `q`, `cid`, `place_id`
- `app/utils/__init__.py` added (exports `sanitize_maps_url`)
- URL validation embedded as `@field_validator` inside `ScraperInput` (checks google.com/maps, goo.gl/maps, maps.app.goo.gl)
- `pyproject.toml` — `[tool.pytest.ini_options] pythonpath = ["."]` and `asyncio_mode = "auto"` added
- `backend/tests/test_utils/test_url_utils.py` — parametrized unit tests for `sanitize_maps_url`

Completed (Task 1.3):
- `app/services/apify_service.py` — async httpx client, actor trigger, polling loop, dataset fetch, parses into `ScraperResponse`
- `app/services/__init__.py` added
- `tests/test_services/test_apify_service.py` — 6 passing tests covering: success, no photos, FAILED, ABORTED, timeout, empty dataset
- All known issues from code review resolved:
  - Import fixed to `from app.config import get_settings`
  - `import os` removed
  - `Authorization` header set once on `AsyncClient` (not duplicated per request)
  - `maxReviews: settings.scraper_max_reviews` passed in actor payload
  - `timeout=30.0` set on `AsyncClient`
  - `get_settings()` called inside function body (not at module level)
  - Response parsed into `ScraperResponse` at service boundary
  - Empty dataset guard added
  - Loguru logging added (run triggered, poll status, success, timeout, error)
  - `str(input.url)` cast added — Pydantic `HttpUrl` is not JSON serializable by default

Completed (Task 1.4) — fully resolved after code review:
- `app/routes/scraper.py` — POST /scrape endpoint, delegates to scrape_maps(), returns ScraperResponse
  - Loguru logging at all four points: request received, job start, job complete, errors
  - HTTPException mapping: TimeoutError→504, RuntimeError→502, ValueError→404, httpx.HTTPStatusError→502
  - `response_model_exclude_none=True` on decorator (null fields stripped from response)
  - Route path is `""` (no trailing slash) under `prefix="/scrape"` — canonical path is `POST /scrape`
  - `str(input.url)` cast used for logging (avoids Pydantic HttpUrl normalization surprises)
- `app/main.py` — CORSMiddleware wired to `settings.cors_origins`, `GET /health` endpoint added, scraper router registered
- `app/routes/__init__.py` — empty file created (namespace package convention)
- `app/services/__init__.py` — re-export pattern removed; routes import directly from `app.services.apify_service`
- `tests/conftest.py` — sets `APIFY_API_KEY` and `GOOGLE_API_KEY` env vars before app import so `get_settings()` succeeds in tests
- `tests/test_routes/test_scraper.py` — 5 passing tests: success (200), invalid URL (422), timeout (504), runtime error (502), no data (404)
- All 21 tests passing across routes, services, and utils

Still pending:
- Tasks 2 (LangChain), 3 (Stripe) not yet started

Architectural decision: `max_reviews` is global config, not user-supplied. Flag as regression if it reappears in `ScraperInput`.

**Why:** One-time payment SaaS model means reliability and correctness matter from the first endpoint — users pay per analysis.

**How to apply:** When reviewing, weight correctness of Pydantic models heavily since they are the contract between all layers. Flag any type-safety gaps early.

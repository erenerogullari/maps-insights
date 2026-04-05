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

Still pending:
- Task 1.4: POST `/scrape` route (`app/routes/scraper.py`) + wire into `main.py`
- Loguru logging in route layer
- `conftest.py` with shared fixtures
- Tasks 2 (LangChain), 3 (Stripe) not yet started

Architectural decision: `max_reviews` is global config, not user-supplied. Flag as regression if it reappears in `ScraperInput`.

**Why:** One-time payment SaaS model means reliability and correctness matter from the first endpoint — users pay per analysis.

**How to apply:** When reviewing, weight correctness of Pydantic models heavily since they are the contract between all layers. Flag any type-safety gaps early.

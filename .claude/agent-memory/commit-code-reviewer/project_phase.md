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
- `pyproject.toml` — `[tool.pytest.ini_options] pythonpath = ["."]` added so test imports resolve
- `backend/tests/test_utils/test_url_utils.py` — parametrized unit tests for `sanitize_maps_url`

Still pending (Tasks 1.3–1.4 and beyond):
- Async Apify client (`app/services/apify_service.py`) using httpx
- POST `/scrape` route (`app/routes/scraper.py`)
- `tests/__init__.py` and `tests/test_utils/__init__.py` (missing)
- `conftest.py` with shared fixtures
- Tasks 2 (LangChain), 3 (Stripe) not yet started

Architectural decision: `max_reviews` is global config, not user-supplied. Flag as regression if it reappears in `ScraperInput`.

**Why:** One-time payment SaaS model means reliability and correctness matter from the first endpoint — users pay per analysis.

**How to apply:** When reviewing, weight correctness of Pydantic models heavily since they are the contract between all layers. Flag any type-safety gaps early.

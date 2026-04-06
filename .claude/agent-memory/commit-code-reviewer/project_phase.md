---
name: MapInsights current project phase
description: Current development phase and what has been built so far in the backend
type: project
---

Project is now in Task 2 (LangChain Analysis Chains), actively progressing on branch `backend/ai-feedback`.

Completed so far (Tasks 1 and 2.2 partial):
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
- `app/services/apify_service.py` — async httpx client, actor trigger, polling loop, dataset fetch, parses into `ScraperResponse`
- `app/services/__init__.py` added
- `tests/test_services/test_apify_service.py` — 6 passing tests
- `app/routes/scraper.py` — POST /scrape endpoint, delegates to scrape_maps()
- `app/main.py` — CORSMiddleware wired, GET /health, scraper router registered
- All 21 tests passing across routes, services, and utils

Task 2.2 — Pydantic analysis models added (uncommitted as of 2026-04-06):
- `app/models/analysis.py` — MediaFeedback, InfoFeedback, ReviewFeedback, FeedbackResponse
- `app/models/__init__.py` — updated to export new models
- `pyproject.toml` — langchain, langchain-core, langchain-google-genai added as dependencies
- `app/chains/` directory does NOT yet exist — chain files are still pending
- No tests yet for analysis models

Issues identified in Task 2.2:
- `overall_score` in FeedbackResponse has no `ge=0, le=100` validation constraints (unlike the sub-model scores)
- `generated_at` in FeedbackResponse is not auto-populated with `default_factory=datetime.now` — consumer must set it
- No `video_count` field in MediaFeedback, despite CLAUDE.md describing media as "photos, videos"
- `app/chains/` directory is absent — chains are core to Task 2 but not yet created
- No corresponding tests for analysis models (no `tests/test_models/` or fixtures)

Still pending:
- Task 2: LangChain chains (media_chain, info_chain, review_chain, feedback_chain)
- Task 2: langchain_service.py
- Task 2: analysis route
- Task 3 (Stripe) not yet started

Architectural decision: `max_reviews` is global config, not user-supplied. Flag as regression if it reappears in `ScraperInput`.

**Why:** One-time payment SaaS model means reliability and correctness matter from the first endpoint — users pay per analysis.

**How to apply:** When reviewing, weight correctness of Pydantic models heavily since they are the contract between all layers. Flag any type-safety gaps early.

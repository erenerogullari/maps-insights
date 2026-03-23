---
name: MapInsights current project phase
description: Current development phase and what has been built so far in the backend
type: project
---

Project is in early backend scaffolding phase (Task 1 — Apify Integration).

Completed so far:
- UV initialized, dependencies installed
- `config.py` with pydantic-settings
- `app/main.py` initialized
- `app/models/scraper.py` — Pydantic models for scraper I/O (Subtask 1.1)
- `app/models/__init__.py` added

Still pending (Tasks 1.2–1.4):
- URL validator in `app/utils/validators.py`
- Apify service in `app/services/apify_service.py`
- Scraper route in `app/routes/scraper.py`
- Tasks 2 (LangChain), 3 (Stripe) not yet started

**Why:** One-time payment SaaS model means reliability and correctness matter from the first endpoint — users pay per analysis.

**How to apply:** When reviewing, weight correctness of Pydantic models heavily since they are the contract between all layers. Flag any type-safety gaps early.

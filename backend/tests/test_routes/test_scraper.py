from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models import ScraperResponse

MAPS_URL = "https://maps.google.com/maps?q=starbucks"

MOCK_RESPONSE = ScraperResponse(
    title="Starbucks",
    rating=4.2,
    total_reviews=120,
    phone_number="+1-800-000-0000",
    website="https://starbucks.com",
    address="123 Main St",
)


async def test_scrape_success():
    with patch("app.routes.scraper.scrape_maps", new=AsyncMock(return_value=MOCK_RESPONSE)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/scrape", json={"url": MAPS_URL})

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Starbucks"
    assert data["rating"] == 4.2
    assert data["total_reviews"] == 120
    assert "photos" not in data  # excluded because None + response_model_exclude_none


async def test_scrape_invalid_url():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/scrape", json={"url": "https://example.com/not-maps"})

    assert response.status_code == 422


async def test_scrape_timeout_returns_504():
    with patch(
        "app.routes.scraper.scrape_maps",
        new=AsyncMock(side_effect=TimeoutError("Apify scraping timed out: abc123")),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/scrape", json={"url": MAPS_URL})

    assert response.status_code == 504
    assert "timed out" in response.json()["detail"].lower()


async def test_scrape_runtime_error_returns_502():
    with patch(
        "app.routes.scraper.scrape_maps",
        new=AsyncMock(side_effect=RuntimeError("Apify run FAILED: abc123")),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/scrape", json={"url": MAPS_URL})

    assert response.status_code == 502


async def test_scrape_no_data_returns_404():
    with patch(
        "app.routes.scraper.scrape_maps",
        new=AsyncMock(side_effect=ValueError("No data returned from Apify: abc123")),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/scrape", json={"url": MAPS_URL})

    assert response.status_code == 404
    assert "no data" in response.json()["detail"].lower()

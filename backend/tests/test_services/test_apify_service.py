import pytest
from unittest.mock import patch, MagicMock
from pydantic import HttpUrl
from pytest_httpx import HTTPXMock

from app.services.apify_service import scrape_maps
from app.models import ScraperInput

MAPS_URL = HttpUrl("https://maps.google.com/maps?q=starbucks")
RUN_ID = "abc123"
ACTOR_ID = "apify/google-maps-scraper"
API_KEY = "test-api-key"

MOCK_ITEM = {
    "title": "Starbucks",
    "totalScore": 4.2,
    "reviewsCount": 120,
    "imageUrls": ["https://example.com/photo1.jpg"],
    "reviews": [
        {"author": "Alice", "rating": 5.0, "date": "2024-01-01", "text": "Great!"}
    ],
    "phone": "+1-800-000-0000",
    "website": "https://starbucks.com",
    "address": "123 Main St",
    "openingHours": {"Monday": "6am-9pm"},
}


@pytest.fixture
def mock_settings():
    settings = MagicMock()
    settings.apify_api_key = API_KEY
    settings.apify_actor_id = ACTOR_ID
    settings.apify_timeout_seconds = 10
    settings.scraper_max_reviews = 50
    return settings


@pytest.fixture
def scraper_input():
    return ScraperInput(url=MAPS_URL, include_photos=True)


@pytest.mark.asyncio
async def test_scrape_maps_success(httpx_mock: HTTPXMock, mock_settings, scraper_input):
    httpx_mock.add_response(
        method="POST",
        url=f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs",
        json={"data": {"id": RUN_ID}},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"https://api.apify.com/v2/actor-runs/{RUN_ID}",
        json={"data": {"status": "SUCCEEDED"}},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"https://api.apify.com/v2/actor-runs/{RUN_ID}/dataset/items",
        json=[MOCK_ITEM],
    )

    with patch("app.services.apify_service.get_settings", return_value=mock_settings):
        result = await scrape_maps(scraper_input)

    assert result.title == "Starbucks"
    assert result.rating == 4.2
    assert result.total_reviews == 120
    assert result.phone_number == "+1-800-000-0000"
    assert result.website == "https://starbucks.com"
    assert result.address == "123 Main St"
    assert result.hours == {"Monday": "6am-9pm"}
    assert result.photos is not None
    assert len(result.photos) == 1
    assert str(result.photos[0].url) == "https://example.com/photo1.jpg"


@pytest.mark.asyncio
async def test_scrape_maps_no_photos(httpx_mock: HTTPXMock, mock_settings):
    scraper_input = ScraperInput(url=MAPS_URL, include_photos=False)

    httpx_mock.add_response(
        method="POST",
        url=f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs",
        json={"data": {"id": RUN_ID}},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"https://api.apify.com/v2/actor-runs/{RUN_ID}",
        json={"data": {"status": "SUCCEEDED"}},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"https://api.apify.com/v2/actor-runs/{RUN_ID}/dataset/items",
        json=[MOCK_ITEM],
    )

    with patch("app.services.apify_service.get_settings", return_value=mock_settings):
        result = await scrape_maps(scraper_input)

    assert result.photos is None


@pytest.mark.asyncio
async def test_scrape_maps_actor_failed(
    httpx_mock: HTTPXMock, mock_settings, scraper_input
):
    httpx_mock.add_response(
        method="POST",
        url=f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs",
        json={"data": {"id": RUN_ID}},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"https://api.apify.com/v2/actor-runs/{RUN_ID}",
        json={"data": {"status": "FAILED"}},
    )

    with patch("app.services.apify_service.get_settings", return_value=mock_settings):
        with pytest.raises(RuntimeError, match=f"FAILED.*{RUN_ID}"):
            await scrape_maps(scraper_input)


@pytest.mark.asyncio
async def test_scrape_maps_actor_aborted(
    httpx_mock: HTTPXMock, mock_settings, scraper_input
):
    httpx_mock.add_response(
        method="POST",
        url=f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs",
        json={"data": {"id": RUN_ID}},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"https://api.apify.com/v2/actor-runs/{RUN_ID}",
        json={"data": {"status": "ABORTED"}},
    )

    with patch("app.services.apify_service.get_settings", return_value=mock_settings):
        with pytest.raises(RuntimeError, match=f"ABORTED.*{RUN_ID}"):
            await scrape_maps(scraper_input)


@pytest.mark.asyncio
async def test_scrape_maps_timeout(httpx_mock: HTTPXMock, mock_settings, scraper_input):
    mock_settings.apify_timeout_seconds = 2  # force timeout after first poll

    httpx_mock.add_response(
        method="POST",
        url=f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs",
        json={"data": {"id": RUN_ID}},
    )
    # Keep returning RUNNING so the loop hits the timeout
    httpx_mock.add_response(
        method="GET",
        url=f"https://api.apify.com/v2/actor-runs/{RUN_ID}",
        json={"data": {"status": "RUNNING"}},
    )

    with patch("app.services.apify_service.get_settings", return_value=mock_settings):
        with patch("asyncio.sleep"):  # skip real sleep
            with pytest.raises(TimeoutError, match=RUN_ID):
                await scrape_maps(scraper_input)


@pytest.mark.asyncio
async def test_scrape_maps_empty_dataset(
    httpx_mock: HTTPXMock, mock_settings, scraper_input
):
    httpx_mock.add_response(
        method="POST",
        url=f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs",
        json={"data": {"id": RUN_ID}},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"https://api.apify.com/v2/actor-runs/{RUN_ID}",
        json={"data": {"status": "SUCCEEDED"}},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"https://api.apify.com/v2/actor-runs/{RUN_ID}/dataset/items",
        json=[],
    )

    with patch("app.services.apify_service.get_settings", return_value=mock_settings):
        with pytest.raises(ValueError, match=RUN_ID):
            await scrape_maps(scraper_input)

from httpx import AsyncClient
import asyncio
from loguru import logger
from app.config import get_settings
from app.models import ScraperInput, ScraperResponse, PhotoItem


async def scrape_maps(input: ScraperInput) -> ScraperResponse:
    settings = get_settings()

    async with AsyncClient(
        headers={"Authorization": f"Bearer {settings.apify_api_key}"},
        timeout=30.0,
    ) as client:
        # Run the Apify actor
        response = await client.post(
            f"https://api.apify.com/v2/acts/{settings.apify_actor_id}/runs",
            json={
                "startUrls": [{"url": str(input.url)}],
                "maxReviews": settings.scraper_max_reviews,
            },
        )
        response.raise_for_status()
        run_id = response.json()["data"]["id"]
        logger.info(f"Apify run triggered: {run_id} for url={input.url}")

        # Poll until done or timeout
        timeout = settings.apify_timeout_seconds
        time_elapsed = 0
        while True:
            run_response = await client.get(
                f"https://api.apify.com/v2/actor-runs/{run_id}"
            )
            run_response.raise_for_status()
            status = run_response.json()["data"]["status"]
            logger.debug(f"Apify run {run_id} status={status} elapsed={time_elapsed}s")
            if status == "SUCCEEDED":
                logger.info(f"Apify run {run_id} succeeded after {time_elapsed}s")
                break
            elif status in ("FAILED", "ABORTED", "TIMED-OUT"):
                logger.error(f"Apify run {run_id} ended with status={status}")
                raise RuntimeError(f"Apify run {status}: {run_id}")

            await asyncio.sleep(2)
            time_elapsed += 2
            if time_elapsed >= timeout:
                logger.error(f"Apify run {run_id} timed out after {time_elapsed}s")
                raise TimeoutError(f"Apify scraping timed out: {run_id}")

        # Fetch results
        result_response = await client.get(
            f"https://api.apify.com/v2/actor-runs/{run_id}/dataset/items"
        )
        result_response.raise_for_status()
        response_json = result_response.json()
        if not response_json:
            raise ValueError(f"No data returned from Apify: {run_id}")

        item = response_json[0]
        photos = None
        if input.include_photos and item.get("imageUrls"):
            photos = [PhotoItem(url=u) for u in item["imageUrls"]]

        return ScraperResponse(
            title=item.get("title"),
            rating=item.get("totalScore"),
            photos=photos,
            reviews=item.get("reviews"),
            total_reviews=item.get("reviewsCount"),
            phone_number=item.get("phone"),
            website=item.get("website"),
            address=item.get("address"),
            hours=item.get("openingHours"),
        )

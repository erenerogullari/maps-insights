from fastapi import APIRouter, HTTPException
import httpx
from app.services.apify_service import scrape_maps
from app.models import ScraperInput, ScraperResponse
from loguru import logger

router = APIRouter(prefix="/scrape", tags=["scrape"])


@router.post("", response_model=ScraperResponse, response_model_exclude_none=True)
async def scrape_maps_endpoint(input: ScraperInput) -> ScraperResponse:
    """
    Endpoint to trigger the scraping of Google Maps data.
    """
    url = str(input.url)
    logger.info(f"Starting Apify scrape job for url={url}")
    try:
        result = await scrape_maps(input)
        logger.info(f"Scraping completed for url={url} title={result.title}")
        return result
    except TimeoutError as e:
        logger.error(f"Scraping timed out for url={url}: {e}")
        raise HTTPException(
            status_code=504, detail="Scraping timed out. Please try again."
        )
    except RuntimeError as e:
        logger.error(f"Apify actor failed for url={url}: {e}")
        raise HTTPException(
            status_code=502,
            detail="Scraping failed. The data source returned an error.",
        )
    except ValueError as e:
        logger.warning(f"No data returned for url={url}: {e}")
        raise HTTPException(
            status_code=404, detail="No data found for this Google Maps URL."
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"Upstream HTTP error for url={url}: {e}")
        raise HTTPException(
            status_code=502, detail="Failed to communicate with the scraping service."
        )

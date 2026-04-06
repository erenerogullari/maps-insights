from typing import cast
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger

from app.config import get_settings
from app.models import MediaFeedback, PhotoItem

_SYSTEM = (
    "You are a Google Maps listing analyst. "
    "Evaluate a business's media presence based on the photo data provided "
    "and return structured feedback."
)

_GUIDELINES = (
    "Score the media presence from 0 to 100 using these guidelines:\n"
    "  - 0 photos  → max score ~10  (critical gap, no visual presence)\n"
    "  - 1-4       → max score ~40  (minimal presence)\n"
    "  - 5-9       → max score ~60  (moderate presence)\n"
    "  - 10-19     → max score ~80  (good presence)\n"
    "  - 20+       → up to 100      (penalise if all photos look identical or generic)\n\n"
    "Return:\n"
    "  - score: int (0-100)\n"
    "  - photo_count: the total number of photos (provided below)\n"
    "  - feedback: a short paragraph explaining the score\n"
    "  - recommendations: 2-4 concrete action items "
    "(always include at least one item even if the score is high)"
)


def _build_message(
    title: str, photo_count: int, photos_to_review: list[PhotoItem]
) -> HumanMessage:
    """Build a multimodal HumanMessage with inline images and scoring instructions."""
    content: list[str | dict] = [
        {
            "type": "text",
            "text": (
                f"Business name: {title}\n"
                f"Total photos on listing: {photo_count}\n"
                f"Photos reviewed below ({len(photos_to_review)} of {photo_count}):\n\n"
                f"{_GUIDELINES}"
            ),
        }
    ]

    for i, photo in enumerate(photos_to_review, start=1):
        if photo.description:
            content.append({"type": "text", "text": f"Photo {i}: {photo.description}"})
        content.append({"type": "image_url", "image_url": {"url": str(photo.url)}})

    return HumanMessage(content=content)


async def run_media_chain(
    llm: BaseChatModel, photos: list[PhotoItem] | None, title: str | None
) -> MediaFeedback:
    """Score the media presence of a Google Maps listing using visual analysis.

    Sends up to `settings.max_photos_to_review` images to the LLM for visual
    inspection alongside the total photo count for quantity scoring.

    Args:
        llm: A pre-initialised LangChain chat model (must support vision).
        photos: List of PhotoItem objects from the scraper, or None.
        title: Business name, or None.

    Returns:
        MediaFeedback with score, photo_count, feedback, and recommendations.
    """
    settings = get_settings()
    photo_count = len(photos) if photos else 0
    business = title or "Unknown business"

    logger.info(f"Running media chain for '{business}' with {photo_count} photos")

    photos_to_review = (photos or [])[: settings.max_photos_to_review]

    structured_llm = llm.with_structured_output(MediaFeedback)

    if photos_to_review:
        human_msg = _build_message(business, photo_count, photos_to_review)
    else:
        human_msg = HumanMessage(
            content=(
                f"Business name: {business}\n"
                f"Total photos on listing: 0\n"
                f"No photos are available to review.\n\n"
                f"{_GUIDELINES}"
            )
        )

    messages = [SystemMessage(content=_SYSTEM), human_msg]
    try:
        result = cast(MediaFeedback, await structured_llm.ainvoke(messages))
    except Exception as exc:
        logger.error(f"Media chain LLM call failed for '{business}': {exc}")
        raise

    logger.info(f"Media chain complete for '{business}': score={result.score}")
    return result

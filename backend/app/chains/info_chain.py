from typing import cast
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger

from app.models import ScraperResponse, InfoFeedback

_SYSTEM = (
    "You are a Google Maps listing analyst specialising in information completeness. "
    "You evaluate how fully a business has filled out its Google Maps profile and "
    "provide structured, actionable feedback to help owners improve it."
)

_GUIDELINES = (
    "Scoring rules:\n"
    "  - A deterministic base score has already been computed from field presence:\n"
    "      phone present   → +20 pts\n"
    "      website present → +20 pts\n"
    "      address present → +20 pts\n"
    "      hours present   → +20 pts\n"
    "    Maximum from field presence alone: 80 pts.\n"
    "  - You may award up to 20 additional quality points based on your judgement:\n"
    "      • Hours cover all 7 days and include open/close times\n"
    "      • Website URL looks functional (not a placeholder or broken link)\n"
    "      • Phone number appears valid for its region\n"
    "      • Address is complete (street, city, postcode)\n"
    "  - Your final score MUST be within 5 points of the base score provided below.\n\n"
    "Return:\n"
    "  - score: int (0-100), within 5 pts of the base score\n"
    "  - fields_present: copy the list provided below exactly\n"
    "  - fields_missing: copy the list provided below exactly\n"
    "  - feedback: a short paragraph explaining the score and highlighting the most "
    "important gaps or strengths\n"
    "  - recommendations: 2-4 concrete action items "
    "(always include at least one item even if the score is high)"
)


def _build_message(
    title: str,
    base_score: int,
    fields_present: list[str],
    fields_missing: list[str],
    phone_number: str | None,
    website: str | None,
    address: str | None,
    hours: dict[str, str] | None,
) -> HumanMessage:
    """Build a HumanMessage with pre-computed field data and scoring instructions."""
    hours_text = (
        "\n".join(f"    {day}: {time}" for day, time in hours.items())
        if hours
        else "    (not provided)"
    )

    content = (
        f"Business name: {title}\n\n"
        f"Field presence (deterministic):\n"
        f"  Present: {fields_present or '(none)'}\n"
        f"  Missing: {fields_missing or '(none)'}\n"
        f"  Base score: {base_score}/100\n\n"
        f"Raw field values:\n"
        f"  phone   : {phone_number or '(not provided)'}\n"
        f"  website : {website or '(not provided)'}\n"
        f"  address : {address or '(not provided)'}\n"
        f"  hours   :\n{hours_text}\n\n"
        f"{_GUIDELINES}"
    )

    return HumanMessage(content=content)


def _compute_fields(scraper_data: ScraperResponse) -> tuple[list[str], list[str], int]:
    """Deterministically compute present/missing fields and the base score.

    Returns:
        (fields_present, fields_missing, base_score)
    """
    checks = {
        "phone": scraper_data.phone_number is not None and len(scraper_data.phone_number) >= 1,
        "website": scraper_data.website is not None and len(scraper_data.website) >= 1,
        "address": scraper_data.address is not None and len(scraper_data.address) >= 1,
        "hours": scraper_data.hours is not None and len(scraper_data.hours) >= 1,
    }
    fields_present = [f for f, present in checks.items() if present]
    fields_missing = [f for f, present in checks.items() if not present]
    base_score = len(fields_present) * 20
    return fields_present, fields_missing, base_score


async def run_info_chain(
    llm: BaseChatModel, scraper_data: ScraperResponse
) -> InfoFeedback:
    """Score the information completeness of a Google Maps listing.

    Pre-computes field presence deterministically, then delegates quality
    scoring and feedback generation to the LLM. After the LLM call:
      - fields_present / fields_missing are overwritten with the deterministic values
      - score is clamped to [base_score - 5, base_score + 20] to enforce the spec contract

    Args:
        llm: A pre-initialised LangChain chat model.
        scraper_data: Structured data returned by the Apify scraper.

    Returns:
        InfoFeedback with score, fields_present, fields_missing, feedback,
        and recommendations.
    """
    business = scraper_data.title or "Unknown business"
    fields_present, fields_missing, base_score = _compute_fields(scraper_data)

    logger.info(
        f"Running info chain for '{business}': "
        f"base_score={base_score}, present={fields_present}, missing={fields_missing}"
    )

    human_msg = _build_message(
        title=business,
        base_score=base_score,
        fields_present=fields_present,
        fields_missing=fields_missing,
        phone_number=scraper_data.phone_number,
        website=scraper_data.website,
        address=scraper_data.address,
        hours=scraper_data.hours,
    )

    messages = [SystemMessage(content=_SYSTEM), human_msg]

    structured_llm = llm.with_structured_output(InfoFeedback)
    try:
        result = cast(InfoFeedback, await structured_llm.ainvoke(messages))
    except Exception as exc:
        logger.error(f"Info chain LLM call failed for '{business}': {exc}")
        raise

    # Overwrite fields with deterministic values — do not trust the LLM to copy them correctly.
    result = result.model_copy(update={
        "fields_present": fields_present,
        "fields_missing": fields_missing,
    })

    # Clamp score to the allowed range: base ± 5 pts floor, base + 20 pts ceiling.
    allowed_min = max(0, base_score - 5)
    allowed_max = min(100, base_score + 20)
    if not (allowed_min <= result.score <= allowed_max):
        clamped = max(allowed_min, min(allowed_max, result.score))
        logger.warning(
            f"LLM score {result.score} outside allowed range [{allowed_min}, {allowed_max}] "
            f"for '{business}' — clamping to {clamped}."
        )
        result = result.model_copy(update={"score": clamped})

    logger.info(f"Info chain complete for '{business}': score={result.score}")
    return result

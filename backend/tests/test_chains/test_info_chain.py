import pytest
from unittest.mock import AsyncMock, MagicMock

from app.chains.info_chain import run_info_chain, _compute_fields, _build_message
from app.models.analysis import InfoFeedback
from app.models.scraper import ScraperResponse

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FULL_SCRAPER_DATA = ScraperResponse(
    title="Café Roma",
    phone_number="+44 20 7946 0958",
    website="https://caferoma.co.uk",
    address="12 High Street, London, EC1A 1BB",
    hours={
        "Monday": "8am-6pm",
        "Tuesday": "8am-6pm",
        "Wednesday": "8am-6pm",
        "Thursday": "8am-6pm",
        "Friday": "8am-8pm",
        "Saturday": "9am-5pm",
        "Sunday": "Closed",
    },
)

EMPTY_SCRAPER_DATA = ScraperResponse(title="Ghost Café")

SAMPLE_FEEDBACK = InfoFeedback(
    score=82,
    fields_present=["phone", "website", "address", "hours"],
    fields_missing=[],
    feedback="Excellent information completeness.",
    recommendations=["Consider adding more specific opening hours."],
)


def make_llm(return_value: InfoFeedback = SAMPLE_FEEDBACK) -> MagicMock:
    mock_runnable = MagicMock()
    mock_runnable.ainvoke = AsyncMock(return_value=return_value)
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_runnable
    return mock_llm


# ---------------------------------------------------------------------------
# _compute_fields unit tests
# ---------------------------------------------------------------------------


def test_compute_fields_all_present():
    fp, fm, base = _compute_fields(FULL_SCRAPER_DATA)
    assert set(fp) == {"phone", "website", "address", "hours"}
    assert fm == []
    assert base == 80


def test_compute_fields_none_present():
    fp, fm, base = _compute_fields(EMPTY_SCRAPER_DATA)
    assert fp == []
    assert set(fm) == {"phone", "website", "address", "hours"}
    assert base == 0


def test_compute_fields_partial():
    data = ScraperResponse(title="My Shop", phone_number="+1 555 0100", address="1 Main St")
    fp, fm, base = _compute_fields(data)
    assert set(fp) == {"phone", "address"}
    assert set(fm) == {"website", "hours"}
    assert base == 40


def test_compute_fields_empty_hours_dict_treated_as_missing():
    data = ScraperResponse(title="My Shop", hours={})
    fp, fm, base = _compute_fields(data)
    assert "hours" not in fp
    assert "hours" in fm


def test_compute_fields_empty_string_fields_treated_as_missing():
    data = ScraperResponse(title="My Shop", phone_number="", website="", address="")
    fp, fm, base = _compute_fields(data)
    assert "phone" not in fp
    assert "website" not in fp
    assert "address" not in fp


# ---------------------------------------------------------------------------
# _build_message unit tests
# ---------------------------------------------------------------------------


def test_build_message_embeds_base_score():
    msg = _build_message(
        title="Café Roma",
        base_score=60,
        fields_present=["phone", "website", "address"],
        fields_missing=["hours"],
        phone_number="+44 20 7946 0958",
        website="https://caferoma.co.uk",
        address="12 High Street",
        hours=None,
    )
    assert "60/100" in msg.content  # type: ignore[operator]


def test_build_message_shows_hours_entries():
    msg = _build_message(
        title="My Café",
        base_score=80,
        fields_present=["phone", "website", "address", "hours"],
        fields_missing=[],
        phone_number="+1 555 0100",
        website="https://mycafe.com",
        address="1 Main St",
        hours={"Monday": "9am-5pm"},
    )
    assert "Monday" in msg.content  # type: ignore[operator]
    assert "9am-5pm" in msg.content  # type: ignore[operator]


def test_build_message_no_hours_shows_not_provided():
    msg = _build_message(
        title="My Café",
        base_score=60,
        fields_present=[],
        fields_missing=["hours"],
        phone_number=None,
        website=None,
        address=None,
        hours=None,
    )
    assert "(not provided)" in msg.content  # type: ignore[operator]


# ---------------------------------------------------------------------------
# run_info_chain — field determinism
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_info_chain_overwrites_llm_fields_with_deterministic_values():
    """LLM returns wrong field lists — they must be overwritten."""
    tampered = InfoFeedback(
        score=80,
        fields_present=["phone"],         # LLM got it wrong
        fields_missing=["website", "address", "hours"],
        feedback="Good.",
        recommendations=["Fix something."],
    )
    llm = make_llm(tampered)
    result = await run_info_chain(llm, FULL_SCRAPER_DATA)

    assert set(result.fields_present) == {"phone", "website", "address", "hours"}
    assert result.fields_missing == []


@pytest.mark.asyncio
async def test_run_info_chain_all_fields_present_base_80():
    llm = make_llm(SAMPLE_FEEDBACK)
    result = await run_info_chain(llm, FULL_SCRAPER_DATA)
    assert set(result.fields_present) == {"phone", "website", "address", "hours"}
    assert result.fields_missing == []


@pytest.mark.asyncio
async def test_run_info_chain_no_fields_base_0():
    llm = make_llm(
        InfoFeedback(
            score=2,
            fields_present=[],
            fields_missing=["phone", "website", "address", "hours"],
            feedback="No information provided.",
            recommendations=["Add all fields immediately."],
        )
    )
    result = await run_info_chain(llm, EMPTY_SCRAPER_DATA)
    assert result.fields_present == []
    assert set(result.fields_missing) == {"phone", "website", "address", "hours"}


# ---------------------------------------------------------------------------
# run_info_chain — score clamping
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_info_chain_score_within_range_is_unchanged():
    """base=80, allowed=[75,100]. LLM returns 95 — should pass through."""
    llm = make_llm(SAMPLE_FEEDBACK.model_copy(update={"score": 95}))
    result = await run_info_chain(llm, FULL_SCRAPER_DATA)
    assert result.score == 95


@pytest.mark.asyncio
async def test_run_info_chain_score_clamped_when_too_high():
    """base=80, allowed_max=100. LLM somehow returns 110 — clamp to 100."""
    llm = make_llm(SAMPLE_FEEDBACK.model_copy(update={"score": 110}))
    result = await run_info_chain(llm, FULL_SCRAPER_DATA)
    assert result.score == 100


@pytest.mark.asyncio
async def test_run_info_chain_score_clamped_when_too_low():
    """base=80, allowed_min=75. LLM returns 50 — clamp to 75."""
    llm = make_llm(SAMPLE_FEEDBACK.model_copy(update={"score": 50}))
    result = await run_info_chain(llm, FULL_SCRAPER_DATA)
    assert result.score == 75


@pytest.mark.asyncio
async def test_run_info_chain_score_clamped_for_base_0():
    """base=0, allowed=[0,20]. LLM returns 60 — clamp to 20."""
    llm = make_llm(
        InfoFeedback(
            score=60,
            fields_present=[],
            fields_missing=["phone", "website", "address", "hours"],
            feedback="Nothing here.",
            recommendations=["Add everything."],
        )
    )
    result = await run_info_chain(llm, EMPTY_SCRAPER_DATA)
    assert result.score == 20


# ---------------------------------------------------------------------------
# run_info_chain — LLM failure propagates
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_info_chain_reraises_llm_exception():
    mock_runnable = MagicMock()
    mock_runnable.ainvoke = AsyncMock(side_effect=RuntimeError("LLM unavailable"))
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_runnable

    with pytest.raises(RuntimeError, match="LLM unavailable"):
        await run_info_chain(mock_llm, FULL_SCRAPER_DATA)

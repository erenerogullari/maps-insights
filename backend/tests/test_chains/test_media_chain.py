import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import HttpUrl

from app.chains.media_chain import run_media_chain, _build_message
from app.models.analysis import MediaFeedback
from app.models.scraper import PhotoItem

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SAMPLE_FEEDBACK = MediaFeedback(
    score=72,
    photo_count=5,
    feedback="The business has a decent photo presence.",
    recommendations=["Add interior shots.", "Include photos of your menu."],
)


def make_photo(url: str, description: str | None = None) -> PhotoItem:
    return PhotoItem(url=HttpUrl(url), description=description)


def make_llm(return_value: MediaFeedback = SAMPLE_FEEDBACK) -> MagicMock:
    """Return a mock LLM whose with_structured_output().ainvoke() returns return_value."""
    mock_runnable = MagicMock()
    mock_runnable.ainvoke = AsyncMock(return_value=return_value)
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_runnable
    return mock_llm


def make_settings(max_photos: int = 10) -> MagicMock:
    s = MagicMock()
    s.max_photos_to_review = max_photos
    return s


# ---------------------------------------------------------------------------
# _build_message unit tests
# ---------------------------------------------------------------------------


def test_build_message_includes_image_url_for_each_photo():
    photos = [make_photo("https://example.com/a.jpg"), make_photo("https://example.com/b.jpg")]
    msg = _build_message("Café Roma", photo_count=2, photos_to_review=photos)
    image_blocks = [b for b in msg.content if isinstance(b, dict) and b.get("type") == "image_url"]
    assert len(image_blocks) == 2


def test_build_message_includes_description_text_before_image():
    photos = [make_photo("https://example.com/a.jpg", description="Front entrance")]
    msg = _build_message("Café Roma", photo_count=1, photos_to_review=photos)
    text_blocks = [b for b in msg.content if isinstance(b, dict) and b.get("type") == "text"]
    # First text block is the header; second should be the description
    desc_blocks = [b for b in text_blocks if "Front entrance" in b.get("text", "")]
    assert len(desc_blocks) == 1


def test_build_message_no_description_block_when_description_is_none():
    photos = [make_photo("https://example.com/a.jpg", description=None)]
    msg = _build_message("Café Roma", photo_count=1, photos_to_review=photos)
    text_blocks = [b for b in msg.content if isinstance(b, dict) and b.get("type") == "text"]
    # Only the header text block — no per-photo text block
    assert len(text_blocks) == 1


def test_build_message_embeds_photo_count_in_header():
    photos = [make_photo("https://example.com/a.jpg")]
    msg = _build_message("My Shop", photo_count=42, photos_to_review=photos)
    header = msg.content[0]
    assert isinstance(header, dict)
    assert "42" in header["text"]


# ---------------------------------------------------------------------------
# run_media_chain — zero photos path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_media_chain_zero_photos_uses_text_only_message():
    llm = make_llm(
        MediaFeedback(
            score=5,
            photo_count=0,
            feedback="No photos found.",
            recommendations=["Upload at least one photo immediately."],
        )
    )

    with patch("app.chains.media_chain.get_settings", return_value=make_settings()):
        result = await run_media_chain(llm, photos=None, title="My Shop")

    assert result.score == 5
    assert result.photo_count == 0
    assert len(result.recommendations) >= 1

    # with_structured_output must have been called
    llm.with_structured_output.assert_called_once_with(MediaFeedback)
    # ainvoke must have been called with a list of messages
    call_args = llm.with_structured_output.return_value.ainvoke.call_args
    messages = call_args[0][0]
    # All content should be plain text — no image_url blocks
    for msg in messages:
        if hasattr(msg, "content") and isinstance(msg.content, list):
            image_blocks = [b for b in msg.content if isinstance(b, dict) and b.get("type") == "image_url"]
            assert image_blocks == [], "No image blocks expected when photos=None"


@pytest.mark.asyncio
async def test_run_media_chain_empty_list_treated_as_zero_photos():
    llm = make_llm(
        MediaFeedback(
            score=5,
            photo_count=0,
            feedback="No photos.",
            recommendations=["Add photos."],
        )
    )
    with patch("app.chains.media_chain.get_settings", return_value=make_settings()):
        result = await run_media_chain(llm, photos=[], title="My Shop")

    assert result.photo_count == 0


# ---------------------------------------------------------------------------
# run_media_chain — happy path with photos
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_media_chain_returns_llm_output_unchanged():
    llm = make_llm(SAMPLE_FEEDBACK)
    photos = [make_photo(f"https://example.com/{i}.jpg") for i in range(3)]

    with patch("app.chains.media_chain.get_settings", return_value=make_settings()):
        result = await run_media_chain(llm, photos=photos, title="Café Roma")

    assert result is SAMPLE_FEEDBACK


@pytest.mark.asyncio
async def test_run_media_chain_sends_image_blocks_when_photos_present():
    llm = make_llm(SAMPLE_FEEDBACK)
    photos = [make_photo("https://example.com/a.jpg"), make_photo("https://example.com/b.jpg")]

    with patch("app.chains.media_chain.get_settings", return_value=make_settings()):
        await run_media_chain(llm, photos=photos, title="Café Roma")

    call_args = llm.with_structured_output.return_value.ainvoke.call_args
    messages = call_args[0][0]
    all_content = []
    for msg in messages:
        if hasattr(msg, "content") and isinstance(msg.content, list):
            all_content.extend(msg.content)
    image_blocks = [b for b in all_content if isinstance(b, dict) and b.get("type") == "image_url"]
    assert len(image_blocks) == 2


@pytest.mark.asyncio
async def test_run_media_chain_none_title_defaults_to_unknown_business():
    llm = make_llm(SAMPLE_FEEDBACK)

    with patch("app.chains.media_chain.get_settings", return_value=make_settings()):
        await run_media_chain(llm, photos=None, title=None)

    call_args = llm.with_structured_output.return_value.ainvoke.call_args
    messages = call_args[0][0]
    full_text = " ".join(
        msg.content if isinstance(msg.content, str) else
        " ".join(b.get("text", "") for b in msg.content if isinstance(b, dict))
        for msg in messages
    )
    assert "Unknown business" in full_text


# ---------------------------------------------------------------------------
# run_media_chain — max_photos_to_review cap
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_media_chain_caps_photos_at_max_photos_to_review():
    llm = make_llm(SAMPLE_FEEDBACK)
    photos = [make_photo(f"https://example.com/{i}.jpg") for i in range(20)]

    with patch("app.chains.media_chain.get_settings", return_value=make_settings(max_photos=5)):
        await run_media_chain(llm, photos=photos, title="Big Restaurant")

    call_args = llm.with_structured_output.return_value.ainvoke.call_args
    messages = call_args[0][0]
    all_content = []
    for msg in messages:
        if hasattr(msg, "content") and isinstance(msg.content, list):
            all_content.extend(msg.content)
    image_blocks = [b for b in all_content if isinstance(b, dict) and b.get("type") == "image_url"]
    assert len(image_blocks) == 5


@pytest.mark.asyncio
async def test_run_media_chain_total_count_in_prompt_reflects_full_list_not_cap():
    """Even when capped, the prompt must tell the LLM the real total photo count."""
    llm = make_llm(SAMPLE_FEEDBACK)
    photos = [make_photo(f"https://example.com/{i}.jpg") for i in range(15)]

    with patch("app.chains.media_chain.get_settings", return_value=make_settings(max_photos=3)):
        await run_media_chain(llm, photos=photos, title="My Café")

    call_args = llm.with_structured_output.return_value.ainvoke.call_args
    messages = call_args[0][0]
    all_text = " ".join(
        " ".join(b.get("text", "") for b in msg.content if isinstance(b, dict) and b.get("type") == "text")
        for msg in messages
        if hasattr(msg, "content") and isinstance(msg.content, list)
    )
    assert "15" in all_text

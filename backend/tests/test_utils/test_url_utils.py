import pytest
from app.utils.url_utils import sanitize_maps_url


@pytest.mark.parametrize("input_url, expected", [
    (
        "https://maps.google.com/maps?q=coffee&cid=12345&hl=en&authuser=0",
        "https://maps.google.com/maps?q=coffee&cid=12345",
    ),
    (
        "https://maps.google.com/maps?q=pizza#reviews",
        "https://maps.google.com/maps?q=pizza",
    ),
    (
        "  https://maps.google.com/maps?q=cafe  ",
        "https://maps.google.com/maps?q=cafe",
    ),
    (
        "https://maps.google.com/maps?place_id=ChIJ&hl=en",
        "https://maps.google.com/maps?place_id=ChIJ",
    ),
    (
        "https://maps.google.com/maps?hl=en&authuser=0",
        "https://maps.google.com/maps",
    ),
    (
        "https://maps.google.com/maps/place/Starbucks",
        "https://maps.google.com/maps/place/Starbucks",
    ),
    (
        "https://maps.google.com/maps?cid=12345",
        "https://maps.google.com/maps?cid=12345",
    ),
    (
        "https://maps.google.com/maps?q=sushi&hl=en#photos",
        "https://maps.google.com/maps?q=sushi",
    ),
    ("", ""),
    ("not a url at all", "not a url at all"),
])
def test_sanitize_maps_url(input_url, expected):
    assert sanitize_maps_url(input_url) == expected

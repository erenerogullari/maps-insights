from urllib.parse import urlparse, urlencode, parse_qs, urlunparse

MAPS_KEEP_PARAMS = {"q", "cid", "place_id"}


def sanitize_maps_url(url: str) -> str:
    """
    Sanitize a Google Maps URL by keeping only essential query parameters.

    Args:
        url (str): The original Google Maps URL.

    Returns:
        str: The sanitized Google Maps URL.
    """
    parsed_url = urlparse(url.strip())
    query_params = parse_qs(parsed_url.query)

    # Keep only the essential query parameters
    filtered_params = {k: v for k, v in query_params.items() if k in MAPS_KEEP_PARAMS}

    # Reconstruct the URL with filtered query parameters
    clean_query = urlencode(filtered_params, doseq=True)
    clean_url = urlunparse(parsed_url._replace(query=clean_query, fragment=""))

    return clean_url

import os

# Set required env vars before any app module is imported so that
# get_settings() succeeds without a real .env file during testing.
os.environ.setdefault("APIFY_API_KEY", "test-key")
os.environ.setdefault("GOOGLE_API_KEY", "test-key")

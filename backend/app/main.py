from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import scraper
from app.config import get_settings

settings = get_settings()

app = FastAPI(title="Google Maps Scraper API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scraper.router)


@app.get("/health")
async def health():
    return {"status": "ok"}

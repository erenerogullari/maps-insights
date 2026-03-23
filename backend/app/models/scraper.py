# Pydantic models for scraper data
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime


class ScraperInput(BaseModel):
    url: HttpUrl = Field(description="Google Maps URL to scrape")
    max_reviews: int | None = Field(
        default=None, description="Maximum number of reviews to scrape (default: all)"
    )
    include_photos: bool | None = Field(
        default=True, description="Whether to include photo URLs in the response"
    )


class ReviewItem(BaseModel):
    author: str | None = Field(default=None, description="Author of the review")
    rating: float | None = Field(
        default=None, description="Rating given by the reviewer (0-5)"
    )
    date: datetime | None = Field(default=None, description="Date of the review")
    text: str | None = Field(default=None, description="Text content of the review")


class PhotoItem(BaseModel):
    url: HttpUrl = Field(description="URL of the photo")
    description: str | None = Field(
        default=None, description="Description of the photo"
    )


class ScraperResponse(BaseModel):
    title: str | None = Field(default=None, description="Title of the place")
    rating: float | None = Field(
        default=None, ge=0, le=5, description="Rating of the place (0-5)"
    )
    photos: list[PhotoItem] | None = Field(
        default=None, description="List of photo items"
    )
    reviews: list[ReviewItem] | None = Field(
        default=None, description="List of reviews"
    )
    total_reviews: int | None = Field(
        default=None, description="Total number of reviews"
    )
    phone_number: str | None = Field(
        default=None, description="Phone number of the place"
    )
    website: HttpUrl | None = Field(
        default=None, description="Website URL of the place"
    )
    address: str | None = Field(default=None, description="Address of the place")
    hours: dict[str, str] | None = Field(
        default=None, description="Operating hours of the place"
    )

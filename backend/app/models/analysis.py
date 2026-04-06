from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime, timezone


class MediaFeedback(BaseModel):
    """Output schema for the media analysis chain. Scores photo quantity and quality."""

    score: int = Field(description="Media quality score", ge=0, le=100)
    photo_count: int = Field(description="Number of photos found")
    feedback: str = Field(description="LLM-generated paragraph about media")
    recommendations: list[str] = Field(
        description="2-4 concrete action items to improve media presence"
    )


class InfoFeedback(BaseModel):
    """Output schema for the info completeness chain. Checks contact, hours, website, and other listing fields."""

    score: int = Field(description="Information completeness score", ge=0, le=100)
    fields_present: list[str] = Field(
        description="List of information fields that are present"
    )
    fields_missing: list[str] = Field(
        description="List of information fields that are missing"
    )
    feedback: str = Field(
        description="LLM-generated paragraph about information completeness"
    )
    recommendations: list[str] = Field(
        description="2-4 concrete action items to improve information completeness"
    )


class ReviewFeedback(BaseModel):
    """Output schema for the review analysis chain. Evaluates sentiment, themes, and owner engagement."""

    score: int = Field(description="Review quality score", ge=0, le=100)
    sentiment: Literal["positive", "mixed", "negative"] = Field(
        description="Overall sentiment of the reviews"
    )
    key_themes: list[str] = Field(description="Recurring topics found in reviews")
    owner_response_present: bool = Field(
        description="Whether any owner replies were detected"
    )
    feedback: str = Field(description="LLM-generated paragraph")
    recommendations: list[str] = Field(description="2-4 concrete action items")


class FeedbackResponse(BaseModel):
    """Top-level response returned by the /analyze endpoint. Aggregates all three chain outputs.
    Overall score is a weighted average: media 25%, info 35%, reviews 40%."""

    business_name: str | None = Field(
        default=None, description="Name of the business analyzed"
    )
    overall_score: int = Field(
        description="Weighted average: media 25%, info 35%, reviews 40%", ge=0, le=100
    )
    media: MediaFeedback
    info: InfoFeedback
    reviews: ReviewFeedback
    summary: str = Field(description="2-3 sentence executive summary")
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of when the feedback was generated",
    )

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=8000)

    @field_validator("user_id", "message")
    @classmethod
    def strip_nonempty_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must contain non-whitespace text")
        return value


class RiskAssessment(BaseModel):
    risk_level: Literal["LOW", "CONCERNING", "HIGH"]
    action: str
    dominant_emotion: int | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class GroundingMetadata(BaseModel):
    status: Literal["grounded", "insufficient_data", "unavailable"]
    sources: list[dict[str, Any]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    user_id: str
    response: str
    risk_assessment: RiskAssessment
    grounding: GroundingMetadata
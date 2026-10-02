import logging

from fastapi import APIRouter

from app.core.config import settings
from app.core.db import clear_history, get_recent_history, initialize_database, save_message
from app.schemas.chat import ChatRequest, ChatResponse, GroundingMetadata, RiskAssessment
from app.services.chat_service import conversational_service
from app.services.safety_service import safety_engine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    assessment = safety_engine.evaluate_risk(request.message)
    if assessment.risk_level == "HIGH":
        crisis_response = (
            "I’m really sorry this feels so difficult. I’m an AI support tool, not an "
            "emergency service. "
            f"{settings.crisis_resources}"
        )
        logger.warning("A high-risk keyword intercept was activated; message content was not logged.")
        save_message(request.user_id, "user", request.message)
        save_message(request.user_id, "assistant", crisis_response)
        return ChatResponse(
            user_id=request.user_id,
            response=crisis_response,
            risk_assessment=assessment,
            grounding=GroundingMetadata(status="unavailable", sources=[]),
        )
    return conversational_service.process_user_query(
        request.user_id,
        request.message,
        risk_assessment=assessment,
    )


@router.get("/history/{user_id}")
def conversation_history(user_id: str) -> dict:
    initialize_database()
    return {"user_id": user_id, "messages": get_recent_history(user_id, limit=100)}


@router.delete("/history/{user_id}")
def delete_conversation_history(user_id: str) -> dict[str, str]:
    clear_history(user_id)
    return {"status": "cleared"}
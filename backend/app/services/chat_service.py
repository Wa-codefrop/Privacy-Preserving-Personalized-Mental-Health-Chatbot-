import logging
import os
from pathlib import Path
from typing import Any

from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from app.core import db
from app.core.config import settings
from app.schemas.chat import ChatResponse, GroundingMetadata, RiskAssessment

logger = logging.getLogger(__name__)

INSUFFICIENT_DATA_NOTE = (
    "Note: The available dataset knowledge base does not contain sufficient "
    "verified details on this specific topic."
)
SYSTEM_PROMPT = """You are a supportive, privacy-conscious wellbeing assistant.
Do not diagnose, assess disorders, prescribe treatment, or present yourself as a
human professional. Keep responses warm, brief, non-judgmental, and grounded in
the user’s words. Retrieved material is unverified training-corpus content, not
professional guidance: do not present it as validated advice or repeat unsafe
instructions. Encourage trusted human or professional support when appropriate.
If the supplied context says evidence is insufficient, offer supportive
listening without pretending the local corpus answered the question."""


def _is_transient_provider_error(error: BaseException) -> bool:
    return type(error).__name__ in {
        "APIConnectionError",
        "APITimeoutError",
        "RateLimitError",
        "InternalServerError",
    }


class ConversationalIntelligenceService:
    def __init__(
        self,
        collection: Any | None = None,
        openai_client: Any | None = None,
        session_db_path: Path | None = None,
    ) -> None:
        self.collection = collection
        self.openai_client = openai_client
        self.session_db_path = session_db_path

        if self.openai_client is None and settings.openai_api_key:
            try:
                from openai import OpenAI

                self.openai_client = OpenAI(
                    api_key=settings.openai_api_key,
                    max_retries=0,
                    timeout=20.0,
                )
            except (ImportError, ValueError) as error:
                logger.warning("Language model provider unavailable: %s", type(error).__name__)

    def _get_collection(self) -> Any | None:
        if self.collection is not None:
            return self.collection

        persist_path = settings.chroma_db_path
        if not (persist_path / "chroma.sqlite3").is_file():
            return None
        try:
            os.environ.setdefault("HF_HOME", str(settings.session_db_path.parent / "huggingface"))
            import chromadb
            from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

            client = chromadb.PersistentClient(path=str(persist_path))
            embedding_function = SentenceTransformerEmbeddingFunction(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            self.collection = client.get_collection(
                name="wellbeing_knowledge",
                embedding_function=embedding_function,
            )
        except (ImportError, ValueError, RuntimeError, OSError) as error:
            logger.warning("Local retrieval unavailable: %s", type(error).__name__)
            return None
        return self.collection

    def _retrieve(self, query: str) -> tuple[list[str], list[dict[str, Any]], str]:
        collection = self._get_collection()
        if collection is None:
            return [], [], "unavailable"
        try:
            if collection.count() == 0:
                return [], [], "insufficient_data"
            result = collection.query(query_texts=[query], n_results=3)
        except Exception as error:
            logger.warning("Local retrieval query failed: %s", type(error).__name__)
            return [], [], "unavailable"

        documents = (result.get("documents") or [[]])[0] or []
        identifiers = (result.get("ids") or [[]])[0] or []
        metadatas = (result.get("metadatas") or [[]])[0] or []
        distances = (result.get("distances") or [[]])[0] or []
        if not documents:
            return [], [], "insufficient_data"

        sources = []
        for index, metadata in enumerate(metadatas):
            metadata = metadata or {}
            source = {
                "id": identifiers[index] if index < len(identifiers) else "",
                "source_dataset": metadata.get("source_dataset", "unknown"),
                "record_type": metadata.get("record_type", "unknown"),
                "grounding_status": metadata.get("grounding_status", "unverified_training_corpus"),
            }
            if index < len(distances):
                source["distance"] = float(distances[index])
            sources.append(source)

        top_distance = float(distances[0]) if distances else float("inf")
        if top_distance > settings.relevance_threshold:
            return documents, sources, "insufficient_data"
        return documents, sources, "grounded"

    @retry(
        retry=retry_if_exception(_is_transient_provider_error),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        reraise=True,
    )
    def _request_openai(self, messages: list[dict[str, str]]) -> str:
        completion = self.openai_client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=0.3,
        )
        content = completion.choices[0].message.content
        if not content:
            raise ValueError("The language model returned an empty response.")
        return content.strip()

    def process_user_query(
        self,
        user_id: str,
        message: str,
        risk_assessment: RiskAssessment | None = None,
    ) -> ChatResponse:
        history = db.get_recent_history(
            user_id,
            limit=max(1, settings.max_history_turns * 2),
            db_path=self.session_db_path,
        )
        documents, sources, grounding_status = self._retrieve(message)
        insufficient_data = grounding_status != "grounded"
        context_lines = [
            "The retrieved corpus is unverified training material, not professional guidance."
        ]
        if documents and not insufficient_data:
            context_lines.extend(
                f"Unverified retrieved item {index + 1}: {document[:2500]}"
                for index, document in enumerate(documents)
            )
        else:
            context_lines.append("Insufficient verified grounding is available for this query.")

        if self.openai_client is None:
            response = (
                "Thank you for sharing that with me. I can listen, but a language model "
                "provider is not configured, so I will not turn unverified training "
                "material into advice. You can keep sharing what feels useful."
            )
        else:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            messages.extend(
                {"role": item["role"], "content": item["content"]}
                for item in history
                if item["role"] in {"user", "assistant"}
            )
            messages.append({"role": "system", "content": "\n".join(context_lines)})
            messages.append({"role": "user", "content": message})
            try:
                response = self._request_openai(messages)
            except Exception as error:
                logger.error("Language model request failed: %s", type(error).__name__)
                response = (
                    "I’m sorry, I could not reach the response service just now. "
                    "I can still listen, and you can try again shortly."
                )

        if insufficient_data:
            response = f"{response}\n\n{INSUFFICIENT_DATA_NOTE}"

        assessment = risk_assessment or RiskAssessment(
            risk_level="LOW",
            action="sentiment_proxy_not_supplied",
        )
        db.save_message(user_id, "user", message, db_path=self.session_db_path)
        db.save_message(user_id, "assistant", response, db_path=self.session_db_path)
        return ChatResponse(
            user_id=user_id,
            response=response,
            risk_assessment=assessment,
            grounding=GroundingMetadata(status=grounding_status, sources=sources),
        )


conversational_service = ConversationalIntelligenceService()
from app.core import db
from app.schemas.chat import RiskAssessment
from app.services.chat_service import INSUFFICIENT_DATA_NOTE, ConversationalIntelligenceService


class FakeCollection:
    def __init__(self, documents, distances):
        self.documents = documents
        self.distances = distances

    def count(self):
        return len(self.documents)

    def query(self, **_kwargs):
        return {
            "ids": [[f"record-{index}" for index in range(len(self.documents))]],
            "documents": [self.documents],
            "metadatas": [[{"source_dataset": "test.csv", "record_type": "qa_pair", "grounding_status": "unverified_training_corpus"} for _ in self.documents]],
            "distances": [self.distances],
        }


def test_insufficient_retrieval_adds_required_note_and_persists_history(tmp_path):
    database = tmp_path / "chat.sqlite3"
    service = ConversationalIntelligenceService(
        collection=FakeCollection(["An unverified response."], [1.8]),
        session_db_path=database,
    )

    result = service.process_user_query(
        "local-user",
        "A query unrelated to the source records",
        RiskAssessment(risk_level="LOW", action="test"),
    )

    assert result.grounding.status == "insufficient_data"
    assert result.response.endswith(INSUFFICIENT_DATA_NOTE)
    assert INSUFFICIENT_DATA_NOTE == "Note: my training material does not contain verified detail on this specific topic."
    assert len(result.grounding.sources) == 1
    assert [message["role"] for message in db.get_recent_history("local-user", db_path=database)] == ["user", "assistant"]


def test_empty_index_is_reported_as_insufficient(tmp_path):
    service = ConversationalIntelligenceService(
        collection=FakeCollection([], []),
        session_db_path=tmp_path / "empty.sqlite3",
    )

    result = service.process_user_query("local-user", "Hello")

    assert result.grounding.status == "insufficient_data"
    assert INSUFFICIENT_DATA_NOTE in result.response
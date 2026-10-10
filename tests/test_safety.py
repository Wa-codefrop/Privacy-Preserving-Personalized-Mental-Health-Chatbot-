import numpy as np
import pytest

from app.services.safety_service import SafetyEngine


class FakeVectorizer:
    def transform(self, messages):
        return messages


class FakeClassifier:
    classes_ = np.array([0, 1, 2, 3, 4, 5])

    def __init__(self, probabilities):
        self.probabilities = np.array([probabilities])

    def predict_proba(self, _features):
        return self.probabilities


def test_high_risk_phrase_is_intercepted_without_model(tmp_path):
    engine = SafetyEngine(model_dir=tmp_path)

    assessment = engine.evaluate_risk("I want to end my life")

    assert assessment.risk_level == "HIGH"
    assert assessment.confidence == 1.0


def test_unavailable_sentiment_proxy_does_not_claim_low_risk(tmp_path):
    engine = SafetyEngine(model_dir=tmp_path)

    assessment = engine.evaluate_risk("I have had a hard week")

    assert assessment.risk_level == "ELEVATED"
    assert "unavailable" in assessment.action


def test_configured_sentiment_proxy_signal_is_labeled_elevated(tmp_path):
    engine = SafetyEngine(model_dir=tmp_path)
    engine.vectorizer = FakeVectorizer()
    engine.classifier = FakeClassifier([0.7, 0.05, 0.05, 0.05, 0.1, 0.05])

    assessment = engine.evaluate_risk("A sample message")

    assert assessment.risk_level == "ELEVATED"
    assert assessment.dominant_emotion == 0
    assert assessment.confidence == 0.7


def test_high_risk_keywords_are_matched_case_insensitively(tmp_path):
    engine = SafetyEngine(model_dir=tmp_path)

    assert engine.evaluate_risk("I want to DIE").risk_level == "HIGH"
    assert engine.evaluate_risk("I might hurt myself with self-harm").risk_level == "HIGH"


@pytest.mark.parametrize(
    "message",
    [
        "I am thinking about suicide",
        "I want to kill myself",
        "I want to end my life",
        "I want to die",
        "I might self harm",
    ],
)
def test_every_configured_high_risk_phrase_is_intercepted(tmp_path, message):
    assert SafetyEngine(model_dir=tmp_path).evaluate_risk(message).risk_level == "HIGH"


def test_abuse_disclosure_is_elevated_instead_of_high(tmp_path):
    assessment = SafetyEngine(model_dir=tmp_path).evaluate_risk("I am dealing with abuse")

    assert assessment.risk_level == "ELEVATED"
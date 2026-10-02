import logging
import re
from pathlib import Path

import joblib

from app.core.config import settings
from app.schemas.chat import RiskAssessment

logger = logging.getLogger(__name__)

HIGH_RISK_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bsuicid(?:e|al)\b",
        r"\bkill\s+myself\b",
        r"\bend\s+my\s+life\b",
        r"\bwant\s+to\s+die\b",
        r"\bself[ -]harm\b",
        r"\babuse\b",
    )
)


class SafetyEngine:
    """A deterministic keyword intercept plus an explicitly unvalidated sentiment proxy."""

    def __init__(self, model_dir: Path | None = None) -> None:
        self.model_dir = model_dir or settings.safety_model_dir
        self.vectorizer = None
        self.classifier = None
        vectorizer_path = self.model_dir / "safety_vectorizer.pkl"
        classifier_path = self.model_dir / "safety_classifier.pkl"

        if vectorizer_path.is_file() and classifier_path.is_file():
            try:
                self.vectorizer = joblib.load(vectorizer_path)
                self.classifier = joblib.load(classifier_path)
            except (OSError, ValueError, EOFError, ImportError) as error:
                logger.warning("Safety sentiment proxy unavailable: %s", type(error).__name__)
                self.vectorizer = None
                self.classifier = None

    @property
    def model_available(self) -> bool:
        return self.vectorizer is not None and self.classifier is not None

    def evaluate_risk(self, message: str) -> RiskAssessment:
        if any(pattern.search(message) for pattern in HIGH_RISK_PATTERNS):
            return RiskAssessment(
                risk_level="HIGH",
                action="immediate_support_response_no_external_model_call",
                confidence=1.0,
            )

        if not self.model_available:
            return RiskAssessment(
                risk_level="CONCERNING",
                action="sentiment_proxy_unavailable_encourage_human_support",
            )

        features = self.vectorizer.transform([message])
        probabilities = self.classifier.predict_proba(features)[0]
        class_index = int(probabilities.argmax())
        dominant_emotion = int(self.classifier.classes_[class_index])
        confidence = float(probabilities[class_index])

        if dominant_emotion in {0, 3, 4} and confidence > 0.65:
            return RiskAssessment(
                risk_level="CONCERNING",
                action="sentiment_proxy_signal_encourage_support_not_a_risk_diagnosis",
                dominant_emotion=dominant_emotion,
                confidence=confidence,
            )
        return RiskAssessment(
            risk_level="LOW",
            action="no_high_risk_keyword_or_configured_sentiment_proxy_threshold",
            dominant_emotion=dominant_emotion,
            confidence=confidence,
        )


safety_engine = SafetyEngine()
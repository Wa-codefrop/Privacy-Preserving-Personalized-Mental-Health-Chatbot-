import re
from dataclasses import dataclass

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)")


@dataclass(frozen=True)
class PrivacyPolicy:
    require_consent: bool = False
    local_only: bool = True
    retention_days: int = 30
    allow_external_provider: bool = False
    research_mode: str = "local"


def check_consent(value: str | None) -> bool:
    if value is None:
        return False
    return str(value).strip().lower() in {"yes", "granted", "true", "allow", "consented"}


def scrub_text(value: str) -> str:
    text = str(value)
    text = EMAIL_RE.sub("[EMAIL]", text)
    text = PHONE_RE.sub("[PHONE]", text)
    return text.strip()

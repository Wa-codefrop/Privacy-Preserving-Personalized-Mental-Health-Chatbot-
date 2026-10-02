from typing import Literal

from pydantic import BaseModel


class DatasetStatus(BaseModel):
    present: bool
    files: int


class SafetyModelStatus(BaseModel):
    trained: bool
    accuracy: float | None = None
    macro_f1: float | None = None
    test_rows: int | None = None


class SystemStatus(BaseModel):
    api: Literal["online"]
    database: Literal["connected", "disconnected"]
    dataset: DatasetStatus
    safety_model: SafetyModelStatus
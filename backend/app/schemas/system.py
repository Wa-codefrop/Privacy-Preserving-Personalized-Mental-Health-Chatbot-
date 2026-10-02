from typing import Literal

from pydantic import BaseModel


class DatasetStatus(BaseModel):
    present: bool
    files: int


class SystemStatus(BaseModel):
    api: Literal["online"]
    database: Literal["connected", "disconnected"]
    dataset: DatasetStatus
from fastapi import APIRouter

from app.config import settings
from app.schemas.system import SystemStatus
from app.services.system_status import get_database_status

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/status", response_model=SystemStatus)
def read_system_status() -> SystemStatus:
    dataset_files = sum(
        1
        for path in settings.raw_dataset_dir.rglob("*")
        if path.is_file() and not path.name.startswith(".")
    )
    return SystemStatus(
        api="online",
        database=get_database_status(),
        dataset={"loaded": dataset_files > 0, "files": dataset_files},
    )
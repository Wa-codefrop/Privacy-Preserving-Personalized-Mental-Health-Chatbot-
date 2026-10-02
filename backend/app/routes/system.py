from fastapi import APIRouter

from app.config import settings
from app.schemas.system import SystemStatus
from app.services.dataset_status import count_source_files
from app.services.system_status import get_database_status

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/status", response_model=SystemStatus)
def read_system_status() -> SystemStatus:
    dataset_files = count_source_files(settings.dataset_dir)
    return SystemStatus(
        api="online",
        database=get_database_status(),
        dataset={"present": dataset_files > 0, "files": dataset_files},
    )
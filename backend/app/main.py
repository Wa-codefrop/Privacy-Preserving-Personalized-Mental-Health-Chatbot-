from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.db import initialize_database
from app.routes.chat import router as chat_router
from app.routes.system import router as system_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    initialize_database()
    yield


app = FastAPI(title=settings.app_name, version="0.2.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(system_router, prefix="/api")
app.include_router(chat_router)


@app.get("/health")
def health() -> dict[str, str]:
    from app.services.system_status import get_database_status

    return {"status": "ok", "database": get_database_status()}
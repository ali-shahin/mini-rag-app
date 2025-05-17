from fastapi import APIRouter, Depends
from core.config import get_settings, Settings

base_router = APIRouter(prefix="/api/v1", tags=["base"])


@base_router.get("/")
async def read_root(app_settings: Settings = Depends(get_settings)):
    return {
        "app_name": app_settings.APP_NAME,
        "app_version": app_settings.APP_VERSION,
        "message": "Welcome to the FastAPI application!"
    }

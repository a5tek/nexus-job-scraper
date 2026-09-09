from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.internal import router as internal_router

api_v1_router = APIRouter(prefix="/api/v1")

# Mount sub-routers
api_v1_router.include_router(auth_router)
api_v1_router.include_router(internal_router)


@api_v1_router.get("/health", tags=["Health"])
async def v1_health():
    return {
        "status": "ok",
        "api_version": "v1",
        "service": "nexus-api",
    }

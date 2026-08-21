"""API route registration."""

from fastapi import APIRouter

from app.api.routes.system import router as system_router

router = APIRouter()
router.include_router(system_router)

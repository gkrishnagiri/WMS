"""API route registration."""

from fastapi import APIRouter

from app.api.routes.system import router as system_router
from app.api.routes.warehouse import router as warehouse_router

router = APIRouter()
router.include_router(system_router)
router.include_router(warehouse_router)

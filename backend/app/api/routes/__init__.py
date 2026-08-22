"""API route registration."""

from fastapi import APIRouter

from app.api.routes.ams import router as ams_router
from app.api.routes.ai_config import router as ai_config_router
from app.api.routes.batch import router as batch_router
from app.api.routes.copilot import router as copilot_router
from app.api.routes.operations import router as operations_router
from app.api.routes.monitoring import router as monitoring_router
from app.api.routes.observability import router as observability_router
from app.api.routes.synthetic_users import router as synthetic_users_router
from app.api.routes.system import router as system_router
from app.api.routes.user_reports import router as user_reports_router
from app.api.routes.warehouse import router as warehouse_router

router = APIRouter()
router.include_router(system_router)
router.include_router(warehouse_router)
router.include_router(operations_router)
router.include_router(ams_router)
router.include_router(ai_config_router)
router.include_router(synthetic_users_router)
router.include_router(user_reports_router)
router.include_router(monitoring_router)
router.include_router(observability_router)
router.include_router(batch_router)
router.include_router(copilot_router)

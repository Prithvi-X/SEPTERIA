from fastapi import APIRouter
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.dashboard import router as dashboard_router
from backend.app.api.v1.personnel_self import router as personnel_self_router
from backend.app.api.v1.personnel import router as personnel_router
from backend.app.api.v1.operations import router as operations_router
from backend.app.api.v1.units import router as units_router
from backend.app.api.v1.audit import router as audit_router
from backend.app.api.v1.wellness import router as wellness_router
from backend.app.api.v1.physiology import router as physiology_router
from backend.app.api.v1.predictions import router as predictions_router
from backend.app.api.v1.welfare import router as welfare_router
from backend.app.api.v1.graph import router as graph_router
from backend.app.api.v1.voice import router as voice_router
from backend.app.api.v1.edge import router as edge_router
from backend.app.api.v1.system import router as system_router

api_router = APIRouter()

# Health Check
api_router.include_router(health_router)

# Authentication & RBAC
api_router.include_router(auth_router)

# Phase 3 Personnel Mobile Self-Service (Must precede /personnel/{id})
api_router.include_router(personnel_self_router)

# Phase 2 Authority Management Routers
api_router.include_router(dashboard_router)
api_router.include_router(personnel_router)
api_router.include_router(operations_router)
api_router.include_router(units_router)
api_router.include_router(audit_router)

# Domain Placeholders & Engine Routers
api_router.include_router(wellness_router)
api_router.include_router(physiology_router)
api_router.include_router(predictions_router)
api_router.include_router(welfare_router)
api_router.include_router(graph_router)
api_router.include_router(voice_router)
api_router.include_router(edge_router)
api_router.include_router(system_router)

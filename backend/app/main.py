from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.core.database import Base, engine, SessionLocal
from backend.app.api.router import api_router
from backend.app.models.user import User
from backend.app.core.security import get_password_hash
from shared.constants.roles import UserRole
import backend.app.models # Register all SQLAlchemy models

def seed_default_users():
    """Seeds default demo accounts across all RBAC roles if missing."""
    db = SessionLocal()
    try:
        demo_accounts = [
            ("commander@septeria.mil", "commander123", UserRole.COMMANDER.value, "BSF", "BSF-BN-47"),
            ("medical@septeria.mil", "medical123", UserRole.MEDICAL_OFFICER.value, "BSF", "BSF-BN-47"),
            ("welfare@septeria.mil", "welfare123", UserRole.WELFARE_OFFICER.value, "BSF", "BSF-BN-47"),
            ("soldier@septeria.mil", "soldier123", UserRole.PERSONNEL.value, "BSF", "BSF-BN-47"),
            ("admin@septeria.mil", "admin123", UserRole.ADMIN.value, "BSF", "BSF-BN-47"),
            ("commander@septeria.gov.in", "Commander@1234", UserRole.COMMANDER.value, "BSF", "BSF-BN-47"),
            ("medical@septeria.gov.in", "Medical@1234", UserRole.MEDICAL_OFFICER.value, "BSF", "BSF-BN-47"),
            ("welfare@septeria.gov.in", "Welfare@1234", UserRole.WELFARE_OFFICER.value, "BSF", "BSF-BN-47"),
            ("admin@septeria.gov.in", "Admin@1234", UserRole.ADMIN.value, "BSF", "BSF-BN-47"),
            ("soldier@septeria.gov.in", "Rajesh@1234", UserRole.PERSONNEL.value, "BSF", "BSF-BN-47"),
        ]
        for email, pwd, role, force, unit_id in demo_accounts:
            existing = db.query(User).filter(User.email == email).first()
            if not existing:
                user = User(
                    email=email,
                    hashed_password=get_password_hash(pwd),
                    role=role,
                    force=force,
                    unit_id=unit_id,
                    is_active=True
                )
                db.add(user)
        db.commit()
        logger.info("Default demo accounts checked/seeded successfully.")
    except Exception as e:
        logger.warning(f"Seed users check skipped or failed: {e}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} API in [{settings.APP_ENV}] environment")
    try:
        Base.metadata.create_all(bind=engine)
        seed_default_users()
    except Exception as e:
        logger.warning(f"Database schema auto-creation encountered notice: {e}")
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME} API")

app = FastAPI(
    title="SEPTERIA API",
    description="AI-Based Predictive Personnel Stress and Welfare Monitoring System for Uniformed Forces (SIH26186)",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# CORS Middleware (Support local Next.js, Flutter Web, Vercel, and Railway cloud origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|.*\.vercel\.app|.*\.rlwy\.net|.*\.railway\.app)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "An internal server error occurred",
            "detail": str(exc) if settings.APP_ENV == "development" else None,
        }
    )

# Register v1 API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "project": "SEPTERIA",
        "problem_statement": "SIH26186",
        "description": "AI-Based Predictive Personnel Stress and Welfare Monitoring System for Uniformed Forces",
        "docs_url": f"{settings.API_V1_STR}/docs",
        "health_check": f"{settings.API_V1_STR}/health",
        "model_info": f"{settings.API_V1_STR}/predictions/model-info",
        "contextual_graph": f"{settings.API_V1_STR}/graph/visualization",
        "phase": 7,
    }

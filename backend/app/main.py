from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.departments import router as departments_router
from app.api.doctors import router as doctors_router
from app.api.patients import router as patients_router
from app.api.appointments import router as appointments_router
from app.api.queue import router as queue_router
from app.api.beds import router as beds_router
from app.api.analytics import router as analytics_router
from app.api.ml import router as ml_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="PatientFlow AI — AI Patient Queue Prediction & Bed Management System Modular Monolith API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS Middleware setup
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API Routers
app.include_router(health_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(departments_router, prefix=settings.API_V1_STR)
app.include_router(doctors_router, prefix=settings.API_V1_STR)
app.include_router(patients_router, prefix=settings.API_V1_STR)
app.include_router(appointments_router, prefix=settings.API_V1_STR)
app.include_router(queue_router, prefix=settings.API_V1_STR)
app.include_router(beds_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(ml_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API API docs available at /docs",
        "health": f"{settings.API_V1_STR}/health",
    }

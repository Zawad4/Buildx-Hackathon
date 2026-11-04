from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.seed_data import seed_database
from app.api.routes_auth import router as auth_router
from app.api.routes_customers import router as customers_router
from app.api.routes_audit import router as audit_router
from app.api.routes_pqc import router as pqc_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Automatically ensure database tables and synthetic data exist on startup
    seed_database()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Intelligent, Context-Aware Financial Data Protection System with Post-Quantum Key Establishment",
    version="1.0.0",
    lifespan=lifespan
)

# Explicit CORS Origins for Localhost & 127.0.0.1
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers under /api/v1
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(customers_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(pqc_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["System"])
def health_check():
    """System health check endpoint."""
    return {
        "status": "online",
        "system": settings.PROJECT_NAME,
        "database": "SQLite (Local Vault)",
        "security_layer": "Active"
    }

@app.get("/", tags=["System"])
def root():
    return {
        "message": "Welcome to ADAPTIVE VAULT X Security Core",
        "docs_url": "/docs"
    }

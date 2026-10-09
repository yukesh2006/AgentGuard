"""
AgentGuard - Context-Aware AI Intent Firewall
Phase 6: Persistent Audit Logging & Security Dashboard
"""

import os
import sys
from pathlib import Path

# Ensure 'backend' directory is in sys.path when launched as backend.app.main:app
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.analyze import router as analyze_router
from app.api.risk import router as risk_router
from app.api.decision import router as decision_router
from app.api.intercept import router as intercept_router
from app.api.audit import router as audit_router
from app.api.explain import router as explain_router
from app.api.intelligence import router as intelligence_router
from app.database.database import init_db

# Initialize FastAPI application instance
app = FastAPI(
    title=settings.app_name,
    description=settings.description,
    version=settings.app_version,
)

# Initialize SQLite database schema
init_db()

# Enable CORS: strictly restricted to intended frontend origins
cors_origins = [o for o in settings.cors_origins if o != "*"]
allow_all = "*" in settings.cors_origins

# Optional regex for wildcard Firebase domains (only when explicitly requested)
origin_regex = os.getenv("CORS_ORIGIN_REGEX") or (
    r"^https:\/\/.*\.web\.app$|^https:\/\/.*\.firebaseapp\.com$"
    if os.getenv("CORS_ALLOW_ALL_FIREBASE", "false").lower() in ("true", "1")
    else None
)

from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_all else cors_origins,
    allow_origin_regex=origin_regex,
    allow_credentials=not allow_all,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Enterprise Efficiency: GZip response compression
app.add_middleware(GZipMiddleware, minimum_size=500)


# Enterprise Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Include API routers across all phases
app.include_router(analyze_router)
app.include_router(risk_router)
app.include_router(decision_router)
app.include_router(intercept_router)
app.include_router(audit_router)
app.include_router(explain_router)
app.include_router(intelligence_router)


# Global exception handler to prevent leaking raw tracebacks
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred during request processing."},
    )


@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint indicating that the AgentGuard service is active.
    """
    return {
        "service": "AgentGuard",
        "message": "Context-Aware AI Intent Firewall",
        "status": "running",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint for monitoring service status.
    """
    return {
        "status": "healthy",
        "service": "AgentGuard",
    }

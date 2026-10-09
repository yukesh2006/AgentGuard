"""
AgentGuard - Context-Aware AI Intent Firewall
Phase 6: Persistent Audit Logging & Security Dashboard
"""

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

# Enable CORS for local development and dashboard integration
origins = settings.cors_origins + ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

"""
AgentGuard - Context-Aware AI Intent Firewall
Phase 1 Foundation: Minimal FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI application instance
app = FastAPI(
    title="AgentGuard API",
    description="Context-Aware AI Intent Firewall API",
    version="0.1.0",
)

# Enable CORS for local development and future frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

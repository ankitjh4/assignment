"""
DRINKOO FastAPI Application
Main entry point for the RAG chatbot API.
"""
import logging
import logging.handlers
import os
from pathlib import Path
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from backend.config import Config
from backend.app.routers import auth, chatbot, upload, health

# Configure logging
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format=log_format,
    handlers=[
        logging.StreamHandler(),
        logging.handlers.RotatingFileHandler(
            Config.LOG_FILE,
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=Config.API_TITLE,
    description=Config.API_DESCRIPTION,
    version=Config.API_VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Validate configuration on startup."""
    logger.info("=" * 60)
    logger.info(f"Starting {Config.API_TITLE} v{Config.API_VERSION}")
    logger.info(f"Environment: {Config.ENV}")
    logger.info("=" * 60)
    
    # Validate config
    valid, message = Config.validate()
    if not valid:
        logger.error(f"Configuration error: {message}")
        logger.warning("Starting in degraded mode")
    else:
        logger.info("Configuration validated successfully")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down DRINKOO API")


# Include routers with /api prefix
app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(chatbot.router, prefix="/api")
app.include_router(upload.router, prefix="/api")


# Setup static files for frontend
frontend_dir = Path(__file__).parent.parent.parent / "Frontend"
if frontend_dir.exists():
    # Mount static files (CSS, JS)
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


# API info endpoint
@app.get("/api")
async def api_info():
    """List available API endpoints."""
    return {
        "message": f"Welcome to {Config.API_TITLE} API",
        "version": Config.API_VERSION,
        "endpoints": {
            "health": "/api/health",
            "status": "/api/status",
            "auth": {
                "signup": "POST /api/auth/signup",
                "login": "POST /api/auth/login",
                "logout": "POST /api/auth/logout"
            },
            "chatbot": {
                "ask": "POST /api/chatbot/ask",
                "history": "GET /api/chatbot/history"
            },
            "upload": {
                "image": "POST /api/upload/image",
                "retrieve": "GET /api/upload/image/{filename}"
            }
        },
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


# Root endpoint - serve frontend
@app.get("/")
async def root():
    """Serve the frontend or API info."""
    index_file = frontend_dir / "index.html" if frontend_dir.exists() else None
    if index_file and index_file.exists():
        return FileResponse(index_file)
    
    # Fallback to API info if frontend not available
    return await api_info()


# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle value errors."""
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting development server")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=Config.DEBUG
    )

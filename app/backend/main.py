import os
from pathlib import Path
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
import asyncio

from app.backend.routes import api_router
from app.backend.database.connection import engine
from app.backend.database.models import Base
from app.backend.services.ollama_service import ollama_service
from app.backend.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Hedge Fund API", description="Backend API for AI Hedge Fund", version="0.1.0")

# Initialize database tables (this is safe to run multiple times)
Base.metadata.create_all(bind=engine)

# Load settings (environment variables with optional .env fallback)
settings = get_settings()

# Configure CORS
default_origins = {
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://localhost:5173",
    "https://127.0.0.1:5173",
}

configured_origins = set()

if settings.frontend_origin:
    configured_origins.update(
        origin.strip()
        for origin in settings.frontend_origin.split(",")
        if origin.strip()
    )

if settings.public_url:
    configured_origins.add(settings.public_url.rstrip("/"))

allow_origins = list(default_origins.union(configured_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routes under /api to enable single-origin deployment
app.include_router(api_router, prefix="/api")

# Serve built frontend if available
project_root = Path(__file__).resolve().parents[2]
dist_dir_env = os.getenv("FRONTEND_DIST_DIR")
dist_dir = Path(dist_dir_env) if dist_dir_env else project_root / "app" / "frontend" / "dist"

if dist_dir.exists():
    # Mount the built assets (Vite outputs assets/ and index.html)
    app.mount("/assets", StaticFiles(directory=str(dist_dir / "assets"), html=False), name="assets")

    @app.get("/")
    async def serve_index_root():
        return FileResponse(str(dist_dir / "index.html"))

    # SPA fallback for non-API routes
    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        if full_path.startswith("api/"):
            # Let unmatched API routes 404
            return Response(status_code=404)
        return FileResponse(str(dist_dir / "index.html"))

@app.on_event("startup")
async def startup_event():
    """Startup event to check Ollama availability."""
    try:
        logger.info("Checking Ollama availability...")
        status = await ollama_service.check_ollama_status()
        
        if status["installed"]:
            if status["running"]:
                logger.info(f"✓ Ollama is installed and running at {status['server_url']}")
                if status["available_models"]:
                    logger.info(f"✓ Available models: {', '.join(status['available_models'])}")
                else:
                    logger.info("ℹ No models are currently downloaded")
            else:
                logger.info("ℹ Ollama is installed but not running")
                logger.info("ℹ You can start it from the Settings page or manually with 'ollama serve'")
        else:
            logger.info("ℹ Ollama is not installed. Install it to use local models.")
            logger.info("ℹ Visit https://ollama.com to download and install Ollama")
            
    except Exception as e:
        logger.warning(f"Could not check Ollama status: {e}")
        logger.info("ℹ Ollama integration is available if you install it later")

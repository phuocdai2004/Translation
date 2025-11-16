"""
FastAPI application for Machine Translation and Document Search
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import logging
from fastapi.middleware.cors import CORSMiddleware

from app.routes import translation_routes, search_routes, document_routes, search_web_routes, tts_routes
from app.database import init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Machine Translation & Document Search",
    description="Platform for machine translation and semantic document search",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(translation_routes.router, prefix="/api", tags=["translation"])
app.include_router(search_routes.router, prefix="/api", tags=["search"])
app.include_router(search_web_routes.router, prefix="/api/search", tags=["web-search"])
app.include_router(document_routes.router, prefix="/api", tags=["documents"])
app.include_router(tts_routes.router, tags=["text-to-speech"])

# Mount static files
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    # Mount static files at root for direct access
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Machine Translation & Document Search"
    }


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Machine Translation & Document Search API")
    try:
        # Initialize database
        logger.info("Initializing database...")
        init_db()
        logger.info("✓ Database initialized")
        
        logger.info("Loading translation models...")
        # Models load on-demand in routes, no need to pre-load
        logger.info("Loading search models...")
        logger.info("✓ Services initialized successfully")
    except Exception as e:
        logger.error(f"✗ Error initializing services: {e}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Machine Translation & Document Search API")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

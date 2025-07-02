"""
Spatium API - Network automation and analysis platform.
SSH-based network device configuration retrieval and digital twin deployment.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from spatium.api import device, deployment
from spatium.core.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting Spatium API...")
    yield
    logger.info("Shutting down Spatium API...")


app = FastAPI(
    title="Spatium API",
    description="Network automation and analysis platform for SSH-based device management and digital twin deployment",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["health"])
def root():
    """Root endpoint with API information."""
    return {
        "name": "Spatium",
        "version": settings.APP_VERSION,
        "description": "Spatium API - SSH-only network automation and analysis platform.",
        "docs_url": "/docs",
        "health_check": "/health"
    }


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "service": "spatium-api"
    }


# Include routers
app.include_router(device.router)
app.include_router(deployment.router)
logger.info("Spatium API initialized successfully")

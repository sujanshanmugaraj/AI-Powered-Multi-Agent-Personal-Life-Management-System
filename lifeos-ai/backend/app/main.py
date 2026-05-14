"""
Main FastAPI application entry point for LifeOS AI
Multi-agent system for personalized life management
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.config import settings
from app.database import engine, Base
from app.api import router
from app.api.task_endpoints import task_router

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting LifeOS AI application...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")
    yield
    # Shutdown
    logger.info("Shutting down LifeOS AI application...")

# Create FastAPI app
app = FastAPI(
    title="LifeOS AI - Multi-Agent Life Management",
    description="Collaborative AI agents for personalized daily planning",
    version="0.1.0",
    lifespan=lifespan
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
app.include_router(router.router, prefix="/api/v1", tags=["v1"])
app.include_router(task_router)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "LifeOS AI Backend",
        "version": "0.1.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to LifeOS AI - Collaborative Multi-Agent System",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

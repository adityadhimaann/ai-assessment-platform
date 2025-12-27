"""
AI Assessment Backend - Main Application Entry Point

This FastAPI application provides intelligent evaluation and adaptive question
generation for educational assessments.

Requirements: 8.3, 7.1, 7.2, 7.3, 7.4, 7.5
"""

import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.middleware import register_exception_handlers
from app.routers import assessment, audio
from app.utils.logger import (
    initialize_logging,
    RequestLoggingMiddleware,
    get_logger
)
from config.settings import get_settings


# ============================================================================
# Application Lifecycle Management
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    
    Handles startup and shutdown events:
    - Startup: Validate configuration and initialize logging
    - Shutdown: Cleanup resources
    
    Requirements: 8.3
    """
    # Startup
    logger = get_logger("startup")
    
    try:
        # Initialize logging first
        initialize_logging()
        logger.info("Logging system initialized")
        
        # Validate environment variables by loading settings
        settings = get_settings()
        logger.info(
            "Configuration validated successfully",
            extra={
                "extra_fields": {
                    "gpt_model": settings.gpt_model,
                    "tts_service": settings.tts_service,
                    "server_host": settings.server_host,
                    "server_port": settings.server_port,
                    "log_level": settings.log_level,
                    "max_audio_size_mb": settings.max_audio_size_mb,
                    "session_store_type": settings.session_store_type
                }
            }
        )
        
        logger.info("AI Assessment Backend started successfully")
        
    except Exception as e:
        logger.error(
            f"Failed to start application: {str(e)}",
            extra={"extra_fields": {"error_type": type(e).__name__}}
        )
        # Exit if configuration validation fails
        sys.exit(1)
    
    # Application is running
    yield
    
    # Shutdown
    logger.info("AI Assessment Backend shutting down")


# ============================================================================
# FastAPI Application Setup
# ============================================================================

# Create FastAPI application with lifespan management
app = FastAPI(
    title="AI Assessment Backend",
    description="Intelligent evaluation system with adaptive difficulty",
    version="1.0.0",
    lifespan=lifespan
)


# ============================================================================
# Middleware Configuration
# ============================================================================

# Add request logging middleware (before other middleware)
app.add_middleware(RequestLoggingMiddleware)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register global exception handlers
register_exception_handlers(app)


# ============================================================================
# Router Registration
# ============================================================================

# Register assessment endpoints
app.include_router(
    assessment.router,
    tags=["assessment"]
)

# Register audio endpoints
app.include_router(
    audio.router,
    tags=["audio"]
)


# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.get("/")
async def root():
    """
    Root endpoint - basic health check.
    
    Returns:
        dict: Service status and version information
    """
    return {
        "status": "healthy",
        "service": "AI Assessment Backend",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """
    Detailed health check endpoint.
    
    Returns:
        dict: Detailed health status of all components
    """
    return {
        "status": "healthy",
        "components": {
            "api": "operational",
            "session_store": "operational",
            "logging": "operational"
        }
    }


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    # Get settings for server configuration
    try:
        settings = get_settings()
        host = settings.server_host
        port = settings.server_port
    except Exception as e:
        print(f"Error loading settings: {e}")
        print("Using default host and port")
        host = "0.0.0.0"
        port = 8000
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True
    )

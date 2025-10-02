"""
FastAPI application initialization for Social Media Marketing Dashboard.
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
import logging
import time

from .api import briefs, assets, ideas, creatives, approvals, settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Disable SQLAlchemy engine logs
logging.getLogger('sqlalchemy.engine.Engine').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Social Media Marketing Dashboard API",
    description="API for managing product briefs, assets, creative ideas, and social media content generation",
    version="1.0.0"
)

# CORS middleware - allow frontend on port 3001
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3001/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests"""
    start_time = time.time()
    
    logger.info(f"Request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Add CORS headers to static file responses
    if request.url.path.startswith("/uploads"):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
    
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} | Time: {process_time:.2f}s")
    
    return response


# Error handling
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Validation error", "errors": exc.errors()},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Internal server error", "detail": str(exc)},
    )


# Register API routers
app.include_router(briefs.router)
app.include_router(assets.router)
app.include_router(ideas.router)
app.include_router(creatives.router)
app.include_router(approvals.router)
app.include_router(settings.router)

# Mount static file directories for serving uploaded files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Social Media Marketing Dashboard API"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

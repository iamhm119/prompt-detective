"""
FastAPI main application entry point
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from .core.config import settings
from .api.v1.router import api_router
from .database import engine, Base
from .services.admin_seeder import ensure_super_admin

# Ensure migrations run before interacting with the database
try:
    from run_migrations import run_migrations
except Exception as migration_import_error:  # pragma: no cover - defensive logging
    run_migrations = None
    print(f"⚠️  Could not import run_migrations: {migration_import_error}")

# Create tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if run_migrations:
        try:
            run_migrations()
        except Exception as migration_error:  # pragma: no cover - defensive logging
            print(f"⚠️  Automatic migration failed: {migration_error}")
    Base.metadata.create_all(bind=engine)
    ensure_super_admin()
    yield
    # Shutdown - cleanup if needed

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}

# Serve static files (thumbnails, etc.)
import os
try:
    # Serve thumbnails - from backend/thumbnails directory
    backend_thumbnails_path = os.path.join(os.path.dirname(__file__), "..", "thumbnails")
    backend_thumbnails_path = os.path.abspath(backend_thumbnails_path)
    if os.path.exists(backend_thumbnails_path):
        app.mount("/static/thumbnails", StaticFiles(directory=backend_thumbnails_path), name="thumbnails")
        print(f"✅ Serving thumbnails from: {backend_thumbnails_path}")
    
    # No fallback needed since we removed the root thumbnails directory
        
except Exception as e:
    print(f"Warning: Could not mount static files: {e}")
    pass  # Static directories might not exist in development

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, async_engine
from app.redis import close_redis, init_redis
from app.routers.admin import router as admin_router
from app.routers.check import router as check_router
from app.routers.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown lifecycle events."""
    # Startup
    await init_redis()
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await close_redis()
    await async_engine.dispose()


app = FastAPI(
    title="Rate Limiter Service",
    version="1.0.0",
    description="Centralized rate limiting service for API protection",
    lifespan=lifespan,
)

# Include routers
app.include_router(health_router)
app.include_router(admin_router)
app.include_router(check_router)


@app.get("/")
async def root():
    """Root endpoint returning basic service info."""
    return {
        "service": "Rate Limiter",
        "version": "1.0.0",
        "docs": "/docs",
    }

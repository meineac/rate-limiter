"""Shared fixtures for the Rate Limiter test suite."""

import pytest
import pytest_asyncio
import httpx
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.config import settings


@pytest_asyncio.fixture(autouse=True)
async def setup_app():
    """Create a fresh DB engine + Redis pool for each test.

    The module-level engine in app.database is created at import time and
    bound to a different event loop than the one pytest-asyncio provides.
    We patch the module to use a per-test engine so all async operations
    run on the correct loop.
    """
    import app.database as db_module
    from app.database import Base
    from app.redis import init_redis, close_redis
    import app.models  # noqa: F401 — register models with Base.metadata

    # Create a fresh engine bound to this test's event loop
    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    # Patch the module-level objects so get_db() uses the fresh engine
    db_module.async_engine = engine
    db_module.AsyncSessionLocal = session_factory

    await init_redis()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await close_redis()
    await engine.dispose()


@pytest_asyncio.fixture
async def async_client(setup_app):
    """Create an async HTTP test client bound to the FastAPI app."""
    from app.main import app

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture
def admin_headers():
    """Return authorization headers using the configured admin token."""
    return {"Authorization": f"Bearer {settings.admin_token}"}


@pytest_asyncio.fixture
async def created_service(async_client, admin_headers):
    """Create a test service and return its JSON payload.

    Returned dict contains: service_id, api_key, name, created_at.
    """
    response = await async_client.post(
        "/admin/services",
        json={"name": "test-service"},
        headers=admin_headers,
    )
    assert response.status_code == 201
    return response.json()


@pytest_asyncio.fixture
async def created_rule(async_client, admin_headers, created_service):
    """Create a fixed-window rule for the test service.

    Returned dict contains: rule_id, service_id, api_key, and rule params.
    """
    service_id = created_service["service_id"]
    response = await async_client.post(
        f"/admin/services/{service_id}/rules",
        json={
            "strategy": "fixed_window",
            "limit": 5,
            "window": 60,
            "target": "ip",
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    rule_data = response.json()
    return {
        **rule_data,
        "service_id": service_id,
        "api_key": created_service["api_key"],
    }

"""Tests for the GET /health endpoint."""

import pytest


@pytest.mark.asyncio
async def test_health_returns_200(async_client):
    """GET /health should return 200 with a status field."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_health_contains_dependency_info(async_client):
    """GET /health response should include redis and postgres status fields."""
    response = await async_client.get("/health")
    data = response.json()
    assert "redis" in data
    assert "postgres" in data

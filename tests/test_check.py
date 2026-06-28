"""Tests for the POST /check rate-limiting endpoint."""

import uuid

import pytest


@pytest.mark.asyncio
async def test_check_allowed(async_client, admin_headers, created_rule):
    """A request under the limit should be allowed with correct remaining count."""
    response = await async_client.post(
        "/check",
        json={
            "key": "test-check-allowed",
            "rule_id": created_rule["rule_id"],
        },
        headers={"X-API-Key": created_rule["api_key"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["allowed"] is True
    assert data["remaining"] == 4  # limit=5, first request
    assert "reset_at" in data


@pytest.mark.asyncio
async def test_check_rate_limited(async_client, admin_headers, created_service):
    """After exceeding the limit, the request should be denied."""
    service_id = created_service["service_id"]
    api_key = created_service["api_key"]

    # Create a tight rule: limit=3
    rule_resp = await async_client.post(
        f"/admin/services/{service_id}/rules",
        json={
            "strategy": "fixed_window",
            "limit": 3,
            "window": 60,
            "target": "ip",
        },
        headers=admin_headers,
    )
    assert rule_resp.status_code == 201
    rule_id = rule_resp.json()["rule_id"]

    # Use a unique key so we don't collide with other tests
    check_key = "test-rate-limited-key"

    # First 3 requests should be allowed
    for i in range(3):
        resp = await async_client.post(
            "/check",
            json={"key": check_key, "rule_id": rule_id},
            headers={"X-API-Key": api_key},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["allowed"] is True, f"Request {i + 1} should be allowed"

    # 4th request should be denied
    resp = await async_client.post(
        "/check",
        json={"key": check_key, "rule_id": rule_id},
        headers={"X-API-Key": api_key},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["allowed"] is False
    assert data["remaining"] == 0


@pytest.mark.asyncio
async def test_check_unauthorized_no_header(async_client, created_rule):
    """POST /check without X-API-Key header should return 401 or 422."""
    response = await async_client.post(
        "/check",
        json={
            "key": "test-key",
            "rule_id": created_rule["rule_id"],
        },
    )
    assert response.status_code in (401, 422)


@pytest.mark.asyncio
async def test_check_invalid_api_key(async_client, created_rule):
    """POST /check with an invalid X-API-Key should return 401."""
    response = await async_client.post(
        "/check",
        json={
            "key": "test-key",
            "rule_id": created_rule["rule_id"],
        },
        headers={"X-API-Key": "rlk_invalid_key_000000000000000000"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_check_invalid_rule(async_client, admin_headers, created_service):
    """POST /check with a nonexistent rule_id should return 404."""
    api_key = created_service["api_key"]
    fake_rule_id = str(uuid.uuid4())

    response = await async_client.post(
        "/check",
        json={
            "key": "test-key",
            "rule_id": fake_rule_id,
        },
        headers={"X-API-Key": api_key},
    )
    assert response.status_code == 404

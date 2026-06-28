"""Tests for the admin CRUD endpoints (/admin/services, /admin/services/{id}/rules)."""

import uuid

import pytest





@pytest.mark.asyncio
async def test_create_service(async_client, admin_headers):
    """POST /admin/services should return 201 with service_id and api_key."""
    response = await async_client.post(
        "/admin/services",
        json={"name": "my-new-service"},
        headers=admin_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert "service_id" in data
    assert "api_key" in data
    assert data["api_key"].startswith("rlk_")
    assert data["name"] == "my-new-service"


@pytest.mark.asyncio
async def test_list_services(async_client, admin_headers, created_service):
    """GET /admin/services should include the previously created service."""
    response = await async_client.get(
        "/admin/services",
        headers=admin_headers,
    )
    assert response.status_code == 200
    services = response.json()
    assert isinstance(services, list)
    service_ids = [s["service_id"] for s in services]
    assert created_service["service_id"] in service_ids


@pytest.mark.asyncio
async def test_delete_service(async_client, admin_headers, created_service):
    """DELETE /admin/services/{id} should return 204 and remove the service."""
    service_id = created_service["service_id"]

    # Delete the service
    delete_resp = await async_client.delete(
        f"/admin/services/{service_id}",
        headers=admin_headers,
    )
    assert delete_resp.status_code == 204

    # Verify it no longer appears in the list
    list_resp = await async_client.get(
        "/admin/services",
        headers=admin_headers,
    )
    service_ids = [s["service_id"] for s in list_resp.json()]
    assert service_id not in service_ids





@pytest.mark.asyncio
async def test_create_rule(async_client, admin_headers, created_service):
    """POST /admin/services/{id}/rules should return 201 with rule_id."""
    service_id = created_service["service_id"]
    response = await async_client.post(
        f"/admin/services/{service_id}/rules",
        json={
            "strategy": "fixed_window",
            "limit": 10,
            "window": 60,
            "target": "ip",
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert "rule_id" in data


@pytest.mark.asyncio
async def test_list_rules(async_client, admin_headers, created_rule):
    """GET /admin/services/{id}/rules should include the created rule."""
    service_id = created_rule["service_id"]
    response = await async_client.get(
        f"/admin/services/{service_id}/rules",
        headers=admin_headers,
    )
    assert response.status_code == 200
    rules = response.json()
    assert isinstance(rules, list)
    rule_ids = [r["rule_id"] for r in rules]
    assert created_rule["rule_id"] in rule_ids


@pytest.mark.asyncio
async def test_delete_rule(async_client, admin_headers, created_rule):
    """DELETE /admin/services/{id}/rules/{rule_id} should return 204."""
    service_id = created_rule["service_id"]
    rule_id = created_rule["rule_id"]

    delete_resp = await async_client.delete(
        f"/admin/services/{service_id}/rules/{rule_id}",
        headers=admin_headers,
    )
    assert delete_resp.status_code == 204

    # Verify rule is gone
    list_resp = await async_client.get(
        f"/admin/services/{service_id}/rules",
        headers=admin_headers,
    )
    rule_ids = [r["rule_id"] for r in list_resp.json()]
    assert rule_id not in rule_ids





@pytest.mark.asyncio
async def test_admin_unauthorized_no_header(async_client):
    """POST /admin/services without Authorization header should return 401 or 422."""
    response = await async_client.post(
        "/admin/services",
        json={"name": "should-fail"},
    )
    assert response.status_code in (401, 422)


@pytest.mark.asyncio
async def test_admin_unauthorized_wrong_token(async_client):
    """POST /admin/services with an invalid token should return 401."""
    response = await async_client.post(
        "/admin/services",
        json={"name": "should-fail"},
        headers={"Authorization": "Bearer wrong-token-value"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_invalid_strategy(async_client, admin_headers, created_service):
    """Creating a rule with an invalid strategy should return 422."""
    service_id = created_service["service_id"]
    response = await async_client.post(
        f"/admin/services/{service_id}/rules",
        json={
            "strategy": "invalid",
            "limit": 10,
            "window": 60,
            "target": "ip",
        },
        headers=admin_headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_nonexistent_service(async_client, admin_headers):
    """DELETE /admin/services/{nonexistent} should return 404."""
    fake_id = str(uuid.uuid4())
    response = await async_client.delete(
        f"/admin/services/{fake_id}",
        headers=admin_headers,
    )
    assert response.status_code == 404

# Rate Limiter Service

A centralized, multi-tenant rate limiting service built with **FastAPI**, **Redis**, and **PostgreSQL**. Protect your APIs with configurable rate limiting strategies — no per-service implementation needed.

---

## Features

- **Multi-Tenant Architecture** — Isolate rate limits per service via unique API keys
- **Fixed Window** — Classic time-bucketed counting algorithm
- **Sliding Window** — Weighted combination of current and previous windows for smoother enforcement
- **Redis-Backed** — Sub-millisecond checks via atomic Lua scripts
- **REST API** — Full CRUD for services and rules, plus a single `/check` endpoint
- **Admin Auth** — Bearer-token protected management endpoints
- **Docker Ready** — One-command deployment with `docker-compose`

---

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)

### Run

```bash
git clone https://github.com/meineac/rate-limiter.git
cd rate-limiter

cp .env.example .env

docker-compose up --build
```

The API will be available at **http://localhost:8000**.

Interactive docs are at **http://localhost:8000/docs**.

---

## API Reference

### Health

```bash
curl http://localhost:8000/health
```

```json
{ "status": "ok", "redis": "ok", "postgres": "ok" }
```

### Admin — Services

All admin endpoints require the header:

```
Authorization: Bearer <ADMIN_TOKEN>
```

```bash
# Create a service
curl -X POST http://localhost:8000/admin/services \
  -H "Authorization: Bearer changeme-to-a-secure-token" \
  -H "Content-Type: application/json" \
  -d '{"name": "my-api"}'
```

```json
{
  "service_id": "550e8400-e29b-41d4-a716-446655440000",
  "api_key": "rlk_a1b2c3d4e5f6...",
  "name": "my-api",
  "created_at": "2026-01-01T00:00:00Z"
}
```

```bash
# List all services
curl http://localhost:8000/admin/services \
  -H "Authorization: Bearer changeme-to-a-secure-token"

# Delete a service
curl -X DELETE http://localhost:8000/admin/services/{service_id} \
  -H "Authorization: Bearer changeme-to-a-secure-token"
```

### Admin — Rules

```bash
# Create a rate-limiting rule
curl -X POST http://localhost:8000/admin/services/{service_id}/rules \
  -H "Authorization: Bearer changeme-to-a-secure-token" \
  -H "Content-Type: application/json" \
  -d '{"strategy": "fixed_window", "limit": 100, "window": 60, "target": "ip"}'
```

```json
{ "rule_id": "660e9500-f39c-52e5-b827-557766550000" }
```

```bash
# List rules for a service
curl http://localhost:8000/admin/services/{service_id}/rules \
  -H "Authorization: Bearer changeme-to-a-secure-token"

# Delete a rule
curl -X DELETE http://localhost:8000/admin/services/{service_id}/rules/{rule_id} \
  -H "Authorization: Bearer changeme-to-a-secure-token"
```

### Rate Limit Check

```bash
# Check if a request is allowed
curl -X POST http://localhost:8000/check \
  -H "X-API-Key: rlk_a1b2c3d4e5f6..." \
  -H "Content-Type: application/json" \
  -d '{"key": "192.168.1.1", "rule_id": "660e9500-f39c-52e5-b827-557766550000"}'
```

```json
{
  "allowed": true,
  "remaining": 99,
  "reset_at": 1735689660
}
```

| Field | Type | Description |
|-------|------|-------------|
| `allowed` | `bool` | Whether the request is permitted |
| `remaining` | `int` | Remaining requests in the current window |
| `reset_at` | `int` | Unix timestamp when the window resets |

---

## Architecture

- **PostgreSQL** stores service registrations, API keys, and rate-limiting rules
- **Redis** handles real-time request counting with atomic Lua scripts
- **FastAPI** exposes the admin and check APIs

### Rate Limiting Algorithms

| Algorithm | Description |
|-----------|-------------|
| **Fixed Window** | Divides time into fixed intervals and counts requests per interval. Simple, predictable, but allows burst traffic at window boundaries. |
| **Sliding Window** | Weights the previous window's count by the remaining overlap fraction. Smoother enforcement with no boundary bursts. |

---

## ⚙Configuration

Configuration is managed via environment variables (or a `.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | `redis://redis:6379` | Redis connection URL |
| `DATABASE_URL` | `postgresql+asyncpg://rl_user:password@postgres:5432/ratelimiter` | PostgreSQL connection URL |
| `ADMIN_TOKEN` | `changeme-to-a-secure-token` | Bearer token for admin endpoints |

---

## Development

### Running Locally (without Docker)

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the app (requires Redis and PostgreSQL to be running)
uvicorn app.main:app --reload
```

### Running Tests

Tests require a running Redis and PostgreSQL instance.

```bash
docker-compose up -d redis postgres

export REDIS_URL=redis://localhost:6379
export DATABASE_URL=postgresql+asyncpg://rl_user:password@localhost:5432/ratelimiter

# Run all tests
pytest -v

# Run specific test files
pytest tests/test_health.py -v
pytest tests/test_admin.py -v
pytest tests/test_check.py -v
pytest tests/test_algorithms.py -v
```

---

[Link to the deployed](https://rate-limiter-app-lvqy.onrender.com/)

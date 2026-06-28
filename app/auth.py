"""Authentication dependencies for the Rate Limiter service."""

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Service

# Security schemes — these register in OpenAPI and add the "Authorize" button
_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
_bearer_scheme = HTTPBearer(auto_error=False)


async def verify_api_key(
    api_key: str | None = Depends(_api_key_header),
    db: AsyncSession = Depends(get_db),
) -> Service:
    """Validate the API key and return the associated Service.

    Raises HTTPException 401 if the key is invalid or missing.
    """
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail={"error": "Invalid or missing API key"},
        )
    result = await db.execute(select(Service).where(Service.api_key == api_key))
    service = result.scalars().first()
    if not service:
        raise HTTPException(
            status_code=401,
            detail={"error": "Invalid or missing API key"},
        )
    return service


async def verify_admin_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> None:
    """Validate the admin bearer token.

    Uses FastAPI's HTTPBearer scheme so Swagger UI shows the Authorize
    button and automatically prepends 'Bearer '.
    """
    if not credentials or credentials.credentials != settings.admin_token:
        raise HTTPException(
            status_code=401,
            detail={"error": "Invalid or missing admin token"},
        )

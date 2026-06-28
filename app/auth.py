"""Authentication dependencies for the Rate Limiter service."""

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Service


async def verify_api_key(
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> Service:
    """Validate the API key and return the associated Service.

    Raises HTTPException 401 if the key is invalid or missing.
    """
    result = await db.execute(select(Service).where(Service.api_key == x_api_key))
    service = result.scalars().first()
    if not service:
        raise HTTPException(
            status_code=401,
            detail={"error": "Invalid or missing API key"},
        )
    return service


async def verify_admin_token(
    authorization: str = Header(...),
) -> None:
    """Validate the admin bearer token.

    Expects the header in 'Bearer <token>' format.
    Raises HTTPException 401 if the token is invalid.
    """
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0] != "Bearer" or parts[1] != settings.admin_token:
        raise HTTPException(
            status_code=401,
            detail={"error": "Invalid or missing admin token"},
        )

"""Admin CRUD endpoints for services and rules."""

import secrets
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_admin_token
from app.database import get_db
from app.models import Rule, Service
from app.schemas import (
    RuleCreate,
    RuleListItem,
    RuleResponse,
    ServiceCreate,
    ServiceListItem,
    ServiceResponse,
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(verify_admin_token)],
)



# Service endpoints

@router.post("/services", response_model=ServiceResponse, status_code=201)
async def create_service(
    body: ServiceCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new service with an auto-generated API key."""
    api_key = "rlk_" + secrets.token_hex(16)
    service = Service(name=body.name, api_key=api_key)
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return ServiceResponse(
        service_id=str(service.id),
        name=service.name,
        api_key=service.api_key,
        created_at=service.created_at,
    )


@router.get("/services", response_model=list[ServiceListItem])
async def list_services(db: AsyncSession = Depends(get_db)):
    """List all registered services."""
    result = await db.execute(select(Service))
    services = result.scalars().all()
    return [
        ServiceListItem(
            service_id=str(s.id),
            name=s.name,
            created_at=s.created_at,
        )
        for s in services
    ]


@router.delete("/services/{service_id}", status_code=204)
async def delete_service(
    service_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a service by ID."""
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalars().first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    await db.delete(service)
    await db.commit()



# Rule endpoints

@router.post(
    "/services/{service_id}/rules",
    response_model=RuleResponse,
    status_code=201,
)
async def create_rule(
    service_id: UUID,
    body: RuleCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a rate-limiting rule for a service."""
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalars().first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    rule = Rule(
        service_id=service.id,
        strategy=body.strategy,
        limit=body.limit,
        window=body.window,
        target=body.target,
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return RuleResponse(
        rule_id=str(rule.id),
    )


@router.get(
    "/services/{service_id}/rules",
    response_model=list[RuleListItem],
)
async def list_rules(
    service_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """List all rules for a given service."""
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalars().first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    result = await db.execute(select(Rule).where(Rule.service_id == service_id))
    rules = result.scalars().all()
    return [
        RuleListItem(
            rule_id=str(r.id),
            strategy=r.strategy,
            limit=r.limit,
            window=r.window,
            target=r.target,
            created_at=r.created_at,
        )
        for r in rules
    ]


@router.delete(
    "/services/{service_id}/rules/{rule_id}",
    status_code=204,
)
async def delete_rule(
    service_id: UUID,
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a specific rule."""
    result = await db.execute(select(Rule).where(Rule.id == rule_id))
    rule = result.scalars().first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    await db.delete(rule)
    await db.commit()

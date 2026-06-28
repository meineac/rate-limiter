from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ServiceCreate(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)


class ServiceResponse(BaseModel):
    service_id: str
    api_key: str
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ServiceListItem(BaseModel):
    service_id: str
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RuleCreate(BaseModel):
    strategy: Literal["fixed_window", "sliding_window"]
    limit: int = Field(gt=0)
    window: int = Field(gt=0)
    target: Literal["ip", "key", "endpoint"]

    model_config = ConfigDict(from_attributes=True)


class RuleResponse(BaseModel):
    rule_id: str

    model_config = ConfigDict(from_attributes=True)


class RuleListItem(BaseModel):
    rule_id: str
    strategy: str
    limit: int
    window: int
    target: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CheckRequest(BaseModel):
    key: str
    rule_id: str

    model_config = ConfigDict(from_attributes=True)


class CheckResponse(BaseModel):
    allowed: bool
    remaining: int
    reset_at: int

    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseModel):
    status: str
    redis: str
    postgres: str

    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    error: str

    model_config = ConfigDict(from_attributes=True)

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Service(Base):
    __tablename__ = "services"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    api_key = Column(String(64), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    rules = relationship("Rule", back_populates="service", cascade="all, delete-orphan")


class Rule(Base):
    __tablename__ = "rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id = Column(
        UUID(as_uuid=True), ForeignKey("services.id"), nullable=False
    )
    strategy = Column(String(50), nullable=False)
    limit = Column(Integer, nullable=False)
    window = Column(Integer, nullable=False)  # in seconds
    target = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    service = relationship("Service", back_populates="rules")

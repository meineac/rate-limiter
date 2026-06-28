"""Initial migration: create services and rules tables

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "services",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("api_key", sa.String(64), unique=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_services_api_key", "services", ["api_key"], unique=True)

    op.create_table(
        "rules",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "service_id",
            UUID(as_uuid=True),
            sa.ForeignKey("services.id"),
            nullable=False,
        ),
        sa.Column("strategy", sa.String(50), nullable=False),
        sa.Column("limit", sa.Integer, nullable=False),
        sa.Column("window", sa.Integer, nullable=False),
        sa.Column("target", sa.String(50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_rules_service_id", "rules", ["service_id"])


def downgrade() -> None:
    op.drop_table("rules")
    op.drop_table("services")

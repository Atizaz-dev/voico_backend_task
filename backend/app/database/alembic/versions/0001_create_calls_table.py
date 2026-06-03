"""create calls table

Revision ID: 0001
Revises:
Create Date: 2026-05-23 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "calls",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("phone_number", sqlmodel.AutoString(), nullable=False),
        sa.Column("caller_name", sqlmodel.AutoString(), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("status", sqlmodel.AutoString(), nullable=False),
        sa.Column("summary", sqlmodel.AutoString(), nullable=True),
        sa.Column("label", sqlmodel.AutoString(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("raw_transcript", sqlmodel.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_calls_id"), "calls", ["id"], unique=False)
    op.create_index(op.f("ix_calls_phone_number"), "calls", ["phone_number"], unique=False)
    op.create_index(op.f("ix_calls_status"), "calls", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_calls_status"), table_name="calls")
    op.drop_index(op.f("ix_calls_phone_number"), table_name="calls")
    op.drop_index(op.f("ix_calls_id"), table_name="calls")
    op.drop_table("calls")

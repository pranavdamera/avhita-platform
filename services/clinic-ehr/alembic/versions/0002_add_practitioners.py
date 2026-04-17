"""add practitioners

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-17

Creates: practitioners
Alters:  patients.primary_cardiologist_id → FK to practitioners.id ON DELETE SET NULL
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "practitioners",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("registration_number", sa.String(50), nullable=True),
        sa.Column("family_name", sa.String(255), nullable=False),
        sa.Column("given_names", sa.JSON(), nullable=False),
        sa.Column("specialty", sa.String(100), nullable=True),
        sa.Column("qualification", sa.JSON(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("registration_number", name="uq_practitioners_reg_number"),
    )
    op.create_index(
        "ix_practitioners_registration_number",
        "practitioners",
        ["registration_number"],
    )

    op.create_foreign_key(
        "fk_patient_primary_cardiologist",
        "patients",
        "practitioners",
        ["primary_cardiologist_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_patient_primary_cardiologist", "patients", type_="foreignkey"
    )
    op.drop_index("ix_practitioners_registration_number", table_name="practitioners")
    op.drop_table("practitioners")

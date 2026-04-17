"""initial

Revision ID: 0001
Revises:
Create Date: 2026-04-17

Creates: patients, timeline_events
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "patients",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("abha_id", sa.String(17), nullable=True),
        sa.Column("family_name", sa.String(255), nullable=False),
        sa.Column("given_names", sa.JSON(), nullable=False),
        sa.Column("dob", sa.Date(), nullable=False),
        sa.Column("gender", sa.String(10), nullable=False),
        sa.Column("blood_group", sa.String(5), nullable=True),
        sa.Column("emergency_contact", sa.JSON(), nullable=True),
        sa.Column("primary_cardiologist_id", sa.String(36), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("abha_id", name="uq_patients_abha_id"),
    )
    op.create_index("ix_patients_abha_id", "patients", ["abha_id"])

    op.create_table(
        "timeline_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "patient_id",
            sa.String(36),
            sa.ForeignKey("patients.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(20), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("source_service", sa.String(100), nullable=False),
        sa.Column("structured_data", sa.JSON(), nullable=True),
        sa.Column("summary_text", sa.String(1000), nullable=True),
    )
    op.create_index("ix_timeline_events_patient_id", "timeline_events", ["patient_id"])


def downgrade() -> None:
    op.drop_index("ix_timeline_events_patient_id", table_name="timeline_events")
    op.drop_table("timeline_events")
    op.drop_index("ix_patients_abha_id", table_name="patients")
    op.drop_table("patients")

"""Phase 4 Data Ingestion and Evidence Pipeline Schema

Revision ID: 003_phase4_data_pipeline
Revises: 002_phase2_authority
Create Date: 2026-08-30 19:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '003_phase4_data_pipeline'
down_revision: Union[str, None] = '002_phase2_authority'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Extend physiological_records with SQI, provenance, and motion context
    op.add_column('physiological_records', sa.Column('sqi_status', sa.String(length=20), nullable=False, server_default='GOOD'))
    op.add_column('physiological_records', sa.Column('motion_context', sa.String(length=50), nullable=False, server_default='LOW'))
    op.add_column('physiological_records', sa.Column('source', sa.String(length=50), nullable=False, server_default='synthetic_wearable'))
    op.add_column('physiological_records', sa.Column('device_type', sa.String(length=100), nullable=True, server_default='synthetic_smartband'))
    op.add_column('physiological_records', sa.Column('is_synthetic', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('physiological_records', sa.Column('raw_data_snapshot', sa.JSON(), nullable=True))
    op.add_column('physiological_records', sa.Column('processing_version', sa.String(length=20), nullable=False, server_default='v1.0'))

    # 2. Create missing_intervals table
    op.create_table(
        'missing_intervals',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('personnel_id', sa.String(length=50), nullable=False),
        sa.Column('signal_name', sa.String(length=50), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('duration_minutes', sa.Float(), nullable=False),
        sa.Column('gap_type', sa.String(length=50), nullable=False, server_default='SHORT_GAP'),
        sa.Column('reconstructed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('reconstruction_method', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_missing_intervals_personnel_id', 'missing_intervals', ['personnel_id'])
    op.create_index('ix_missing_intervals_start_time', 'missing_intervals', ['start_time'])

    # 3. Create environmental_records table
    op.create_table(
        'environmental_records',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('location', sa.String(length=255), nullable=False),
        sa.Column('unit_id', sa.String(length=50), nullable=True),
        sa.Column('ambient_temp', sa.Float(), nullable=False),
        sa.Column('altitude', sa.Float(), nullable=True),
        sa.Column('humidity', sa.Float(), nullable=True),
        sa.Column('environment_category', sa.String(length=100), nullable=False),
        sa.Column('incident_phase', sa.String(length=100), nullable=False, server_default='ROUTINE'),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_environmental_records_location', 'environmental_records', ['location'])
    op.create_index('ix_environmental_records_timestamp', 'environmental_records', ['timestamp'])

def downgrade() -> None:
    op.drop_table('environmental_records')
    op.drop_table('missing_intervals')
    op.drop_column('physiological_records', 'processing_version')
    op.drop_column('physiological_records', 'raw_data_snapshot')
    op.drop_column('physiological_records', 'is_synthetic')
    op.drop_column('physiological_records', 'device_type')
    op.drop_column('physiological_records', 'source')
    op.drop_column('physiological_records', 'motion_context')
    op.drop_column('physiological_records', 'sqi_status')

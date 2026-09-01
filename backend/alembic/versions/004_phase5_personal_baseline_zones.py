"""Phase 5 Personal Baseline and 3-Zone Intelligence Schema

Revision ID: 004_phase5_personal_baseline_zones
Revises: 003_phase4_data_pipeline
Create Date: 2026-08-30 20:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '004_phase5_personal_baseline_zones'
down_revision: Union[str, None] = '003_phase4_data_pipeline'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Extend baselines table with robust stats and provenance
    op.add_column('baselines', sa.Column('median', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('baselines', sa.Column('mad', sa.Float(), nullable=False, server_default='1.0'))
    op.add_column('baselines', sa.Column('p10', sa.Float(), nullable=True))
    op.add_column('baselines', sa.Column('p90', sa.Float(), nullable=True))
    op.add_column('baselines', sa.Column('mean', sa.Float(), nullable=True))
    op.add_column('baselines', sa.Column('std', sa.Float(), nullable=True))
    op.add_column('baselines', sa.Column('observation_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('baselines', sa.Column('coverage_pct', sa.Float(), nullable=False, server_default='100.0'))
    op.add_column('baselines', sa.Column('quality_rating', sa.String(length=20), nullable=False, server_default='GOOD'))
    op.add_column('baselines', sa.Column('is_cohort_prior', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('baselines', sa.Column('context_modifiers', sa.JSON(), nullable=True))
    op.create_index('ix_baselines_metric', 'baselines', ['metric'])

    # 2. Create personal_state_snapshots table
    op.create_table(
        'personal_state_snapshots',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('personnel_id', sa.String(length=50), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('operational_zone', sa.String(length=100), nullable=False),
        sa.Column('duty_type', sa.String(length=100), nullable=False),
        sa.Column('shift', sa.String(length=100), nullable=False),
        sa.Column('baseline_snapshot', sa.JSON(), nullable=False),
        sa.Column('deviations', sa.JSON(), nullable=False),
        sa.Column('trajectories', sa.JSON(), nullable=False),
        sa.Column('recovery_burden_score', sa.Float(), nullable=False),
        sa.Column('recovery_burden_factors', sa.JSON(), nullable=False),
        sa.Column('rebound_status', sa.String(length=50), nullable=False, server_default='NONE'),
        sa.Column('transition_state', sa.String(length=50), nullable=False, server_default='NONE'),
        sa.Column('evidence_quality', sa.String(length=20), nullable=False, server_default='GOOD'),
        sa.Column('attribution_summary', sa.String(length=500), nullable=False),
        sa.Column('processing_version', sa.String(length=20), nullable=False, server_default='v1.0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_personal_state_snapshots_personnel_id', 'personal_state_snapshots', ['personnel_id'])
    op.create_index('ix_personal_state_snapshots_timestamp', 'personal_state_snapshots', ['timestamp'])

    # 3. Create recovery_debt_snapshots table
    op.create_table(
        'recovery_debt_snapshots',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('personnel_id', sa.String(length=50), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('debt_score', sa.Float(), nullable=False),
        sa.Column('sleep_deficit_hours', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('hrv_suppression_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rhr_elevation_bpm', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('consecutive_high_workload_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('contributing_factors', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_recovery_debt_snapshots_personnel_id', 'recovery_debt_snapshots', ['personnel_id'])
    op.create_index('ix_recovery_debt_snapshots_timestamp', 'recovery_debt_snapshots', ['timestamp'])

def downgrade() -> None:
    op.drop_table('recovery_debt_snapshots')
    op.drop_table('personal_state_snapshots')
    op.drop_index('ix_baselines_metric', 'baselines')
    op.drop_column('baselines', 'context_modifiers')
    op.drop_column('baselines', 'is_cohort_prior')
    op.drop_column('baselines', 'quality_rating')
    op.drop_column('baselines', 'coverage_pct')
    op.drop_column('baselines', 'observation_count')
    op.drop_column('baselines', 'std')
    op.drop_column('baselines', 'mean')
    op.drop_column('baselines', 'p90')
    op.drop_column('baselines', 'p10')
    op.drop_column('baselines', 'mad')
    op.drop_column('baselines', 'median')

"""Initial schema for SEPTERIA Phase 1

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-29 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Users Table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('force', sa.String(length=50), nullable=True),
        sa.Column('unit_id', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_id', 'users', ['id'])

    # Units Table
    op.create_table(
        'units',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('code', sa.String(length=50), nullable=False, unique=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('force', sa.String(length=50), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=False),
        sa.Column('zone', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_units_code', 'units', ['code'])
    op.create_index('ix_units_id', 'units', ['id'])

    # Personnel Table
    op.create_table(
        'personnel',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('personnel_id', sa.String(length=50), nullable=False, unique=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('force', sa.String(length=50), nullable=False),
        sa.Column('unit_id', sa.String(length=50), nullable=False),
        sa.Column('role', sa.String(length=100), nullable=False),
        sa.Column('rank', sa.String(length=100), nullable=True),
        sa.Column('posting', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_personnel_personnel_id', 'personnel', ['personnel_id'])
    op.create_index('ix_personnel_unit_id', 'personnel', ['unit_id'])
    op.create_index('ix_personnel_id', 'personnel', ['id'])

    # Operational Contexts Table
    op.create_table(
        'operational_contexts',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('personnel_id', sa.String(length=50), nullable=True),
        sa.Column('unit_id', sa.String(length=50), nullable=True),
        sa.Column('zone', sa.String(length=100), nullable=False),
        sa.Column('duty_type', sa.String(length=100), nullable=False),
        sa.Column('shift', sa.String(length=100), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=False),
        sa.Column('environment', sa.String(length=100), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('temporary', sa.Boolean(), nullable=False, default=False),
        sa.Column('auto_revert', sa.Boolean(), nullable=False, default=True),
        sa.Column('source', sa.String(length=50), nullable=False, default='AUTHORITY'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_operational_contexts_personnel_id', 'operational_contexts', ['personnel_id'])
    op.create_index('ix_operational_contexts_unit_id', 'operational_contexts', ['unit_id'])
    op.create_index('ix_operational_contexts_id', 'operational_contexts', ['id'])

    # Assignments Table
    op.create_table(
        'assignments',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('personnel_id', sa.String(length=50), nullable=True),
        sa.Column('unit_id', sa.String(length=50), nullable=True),
        sa.Column('context_id', sa.String(length=36), sa.ForeignKey('operational_contexts.id'), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('auto_revert', sa.Boolean(), nullable=False, default=True),
        sa.Column('status', sa.String(length=50), nullable=False, default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_assignments_id', 'assignments', ['id'])

    # Wellness Records Table
    op.create_table(
        'wellness_records',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('personnel_id', sa.String(length=50), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('fatigue', sa.Integer(), nullable=False),
        sa.Column('stress', sa.Integer(), nullable=False),
        sa.Column('mood', sa.Integer(), nullable=False),
        sa.Column('sleep_quality', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('evidence_status', sa.String(length=50), nullable=False, default='OBSERVED'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_wellness_records_personnel_id', 'wellness_records', ['personnel_id'])
    op.create_index('ix_wellness_records_timestamp', 'wellness_records', ['timestamp'])
    op.create_index('ix_wellness_records_id', 'wellness_records', ['id'])

    # Physiological Records Table
    op.create_table(
        'physiological_records',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('personnel_id', sa.String(length=50), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('hr', sa.Float(), nullable=False),
        sa.Column('hrv', sa.Float(), nullable=False),
        sa.Column('resting_hr', sa.Float(), nullable=False),
        sa.Column('sleep', sa.Float(), nullable=False),
        sa.Column('activity', sa.Float(), nullable=False),
        sa.Column('respiration', sa.Float(), nullable=True),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('signal_quality', sa.Float(), nullable=False, default=1.0),
        sa.Column('evidence_status', sa.String(length=50), nullable=False, default='OBSERVED'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_physiological_records_personnel_id', 'physiological_records', ['personnel_id'])
    op.create_index('ix_physiological_records_timestamp', 'physiological_records', ['timestamp'])
    op.create_index('ix_physiological_records_id', 'physiological_records', ['id'])

    # Baselines Table
    op.create_table(
        'baselines',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('personnel_id', sa.String(length=50), nullable=False),
        sa.Column('metric', sa.String(length=100), nullable=False),
        sa.Column('baseline_statistics', sa.JSON(), nullable=False),
        sa.Column('update_timestamp', sa.DateTime(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, default=1.0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_baselines_personnel_id', 'baselines', ['personnel_id'])
    op.create_index('ix_baselines_id', 'baselines', ['id'])

    # Predictions Table
    op.create_table(
        'predictions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('personnel_id', sa.String(length=50), nullable=False),
        sa.Column('risk_level', sa.String(length=50), nullable=False, default='LOW'),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('trajectory', sa.String(length=50), nullable=False, default='STABLE'),
        sa.Column('contributing_factors', sa.JSON(), nullable=False),
        sa.Column('evidence_status', sa.String(length=50), nullable=False, default='INFERRED'),
        sa.Column('model_version', sa.String(length=100), nullable=False, default='xgb-proto-v1.0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_predictions_personnel_id', 'predictions', ['personnel_id'])
    op.create_index('ix_predictions_created_at', 'predictions', ['created_at'])
    op.create_index('ix_predictions_id', 'predictions', ['id'])

    # Recommendations Table
    op.create_table(
        'recommendations',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('personnel_id', sa.String(length=50), nullable=False),
        sa.Column('type', sa.String(length=100), nullable=False),
        sa.Column('priority', sa.String(length=50), nullable=False, default='ROUTINE'),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, default='PENDING'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_recommendations_personnel_id', 'recommendations', ['personnel_id'])
    op.create_index('ix_recommendations_id', 'recommendations', ['id'])

    # Audit Logs Table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('actor_id', sa.String(length=50), nullable=False),
        sa.Column('actor_role', sa.String(length=50), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('object_type', sa.String(length=100), nullable=False),
        sa.Column('object_id', sa.String(length=100), nullable=True),
        sa.Column('details', sa.JSON(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('outcome', sa.String(length=50), nullable=False, default='SUCCESS'),
    )
    op.create_index('ix_audit_logs_actor_id', 'audit_logs', ['actor_id'])
    op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'])
    op.create_index('ix_audit_logs_id', 'audit_logs', ['id'])

def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('recommendations')
    op.drop_table('predictions')
    op.drop_table('baselines')
    op.drop_table('physiological_records')
    op.drop_table('wellness_records')
    op.drop_table('assignments')
    op.drop_table('operational_contexts')
    op.drop_table('personnel')
    op.drop_table('units')
    op.drop_table('users')

"""Phase 2 Authority Management Schema

Revision ID: 002_phase2_authority
Revises: 001_initial_schema
Create Date: 2026-08-30 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_phase2_authority'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Extend operational_contexts
    op.add_column('operational_contexts', sa.Column('name', sa.String(length=255), nullable=True))
    op.add_column('operational_contexts', sa.Column('status', sa.String(length=50), nullable=False, server_default='ACTIVE'))
    op.add_column('operational_contexts', sa.Column('previous_context_snapshot', sa.JSON(), nullable=True))
    op.add_column('operational_contexts', sa.Column('notes', sa.Text(), nullable=True))

    # 2. Extend personnel
    op.add_column('personnel', sa.Column('active_context_id', sa.String(length=36), nullable=True))
    op.add_column('personnel', sa.Column('leave_status', sa.String(length=50), nullable=False, server_default='NONE'))
    op.add_column('personnel', sa.Column('leave_end_date', sa.DateTime(), nullable=True))
    op.add_column('personnel', sa.Column('return_date', sa.DateTime(), nullable=True))
    op.add_column('personnel', sa.Column('transition_start_date', sa.DateTime(), nullable=True))

    # Foreign key for active_context_id
    op.create_foreign_key(
        'fk_personnel_active_context',
        'personnel',
        'operational_contexts',
        ['active_context_id'],
        ['id']
    )

    # 3. Create leave_events table
    op.create_table(
        'leave_events',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('personnel_id', sa.String(length=50), nullable=False),
        sa.Column('leave_type', sa.String(length=100), nullable=False, server_default='ANNUAL_LEAVE'),
        sa.Column('leave_start_date', sa.DateTime(), nullable=True),
        sa.Column('leave_end_date', sa.DateTime(), nullable=False),
        sa.Column('return_date', sa.DateTime(), nullable=False),
        sa.Column('transition_days_total', sa.Integer(), nullable=False, server_default='14'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='ACTIVE_TRANSITION'),
        sa.Column('recorded_by', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_leave_events_personnel_id', 'leave_events', ['personnel_id'])

def downgrade() -> None:
    op.drop_table('leave_events')
    op.drop_constraint('fk_personnel_active_context', 'personnel', type_='foreignkey')
    op.drop_column('personnel', 'transition_start_date')
    op.drop_column('personnel', 'return_date')
    op.drop_column('personnel', 'leave_end_date')
    op.drop_column('personnel', 'leave_status')
    op.drop_column('personnel', 'active_context_id')
    op.drop_column('operational_contexts', 'notes')
    op.drop_column('operational_contexts', 'previous_context_snapshot')
    op.drop_column('operational_contexts', 'status')
    op.drop_column('operational_contexts', 'name')

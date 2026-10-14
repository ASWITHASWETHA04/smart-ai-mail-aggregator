"""Initial schema for users and email_generation_events

Revision ID: 001_initial_schema
Revises: None
Create Date: 2026-10-14 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 1. Create 'users' table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=32), nullable=False, server_default='user'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. Create 'email_generation_events' table
    op.create_table(
        'email_generation_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('event_type', sa.String(length=64), nullable=False),
        sa.Column('category', sa.String(length=64), nullable=False),
        sa.Column('tone', sa.String(length=32), nullable=False),
        sa.Column('language', sa.String(length=32), nullable=False),
        sa.Column('length', sa.String(length=32), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('prompt_tokens', sa.Integer(), nullable=True),
        sa.Column('completion_tokens', sa.Integer(), nullable=True),
        sa.Column('total_tokens', sa.Integer(), nullable=True),
        sa.Column('error_code', sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_email_generation_events_category'), 'email_generation_events', ['category'], unique=False)
    op.create_index(op.f('ix_email_generation_events_created_at'), 'email_generation_events', ['created_at'], unique=False)
    op.create_index(op.f('ix_email_generation_events_status'), 'email_generation_events', ['status'], unique=False)
    op.create_index(op.f('ix_email_generation_events_user_id'), 'email_generation_events', ['user_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_email_generation_events_user_id'), table_name='email_generation_events')
    op.drop_index(op.f('ix_email_generation_events_status'), table_name='email_generation_events')
    op.drop_index(op.f('ix_email_generation_events_created_at'), table_name='email_generation_events')
    op.drop_index(op.f('ix_email_generation_events_category'), table_name='email_generation_events')
    op.drop_table('email_generation_events')

    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

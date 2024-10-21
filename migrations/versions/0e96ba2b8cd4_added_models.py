"""Added Models

Revision ID: 0e96ba2b8cd4
Revises: 
Create Date: 2024-10-15 14:08:25.778311

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '0e96ba2b8cd4'
down_revision = None
branch_labels = None
depends_on = None


def table_exists(table_name):
    bind = op.get_bind()
    result = bind.execute(text(f"SELECT to_regclass('{table_name}');")).scalar()
    return result is not None


def upgrade():
    # Create the 'tags' table if it doesn't exist
    if not table_exists('tags'):
        op.create_table('tags',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('name', sa.String(length=50), nullable=False, unique=True),
            sa.Column('created_at', sa.DateTime(), nullable=True)
        )
    
    # Create the 'users' table if it doesn't exist
    if not table_exists('users'):
        op.create_table('users',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('username', sa.String(length=50), nullable=False, unique=True),
            sa.Column('email', sa.String(length=120), nullable=False, unique=True),
            sa.Column('password_hash', sa.String(length=128), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True)
        )

    # Create the 'entries' table if it doesn't exist
    if not table_exists('entries'):
        op.create_table('entries',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('location', sa.String(length=100), nullable=False),
            sa.Column('date', sa.DateTime(), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'])
        )

    # Create the 'entry_tags' table if it doesn't exist
    if not table_exists('entry_tags'):
        op.create_table('entry_tags',
            sa.Column('entry_id', sa.Integer(), nullable=False),
            sa.Column('tag_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['entry_id'], ['entries.id']),
            sa.ForeignKeyConstraint(['tag_id'], ['tags.id']),
            sa.PrimaryKeyConstraint('entry_id', 'tag_id')
        )

    # Create the 'photos' table if it doesn't exist
    if not table_exists('photos'):
        op.create_table('photos',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('url', sa.String(length=200), nullable=False),
            sa.Column('entry_id', sa.Integer(), nullable=False),
            sa.Column('uploaded_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['entry_id'], ['entries.id'])
        )


def downgrade():
    # Drop tables in reverse order of creation
    op.drop_table('photos')
    op.drop_table('entry_tags')
    op.drop_table('entries')
    op.drop_table('users')
    op.drop_table('tags')

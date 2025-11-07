"""Initial migration

Revision ID: 5af10c03069b
Revises:
Create Date: 2025-11-05 20:18:40.764239
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5af10c03069b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Creating the 'location' table
    op.create_table(
        'location',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('country_code', sa.String(2), nullable=False),
        sa.Column('city_slug', sa.String(), nullable=True),
        sa.Column('order_index', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.CheckConstraint("city_slug IS NULL OR city_slug ~ '^[a-z0-9-]+$'", name='ck_location_city_slug'),
        sa.CheckConstraint("country_code ~ '^[A-Z]{2}$'", name='ck_location_country_code_iso2'),
        sa.CheckConstraint('order_index >= 0', name='ck_location_order_nonneg'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('country_code', 'city_slug', name='uq_location_country_city')
    )
    op.create_index('ix_location_city_slug', 'location', ['city_slug'], unique=False)
    op.create_index('ix_location_country_code', 'location', ['country_code'], unique=False)
    op.create_index('ix_location_i18n_order_index', 'location_i18n', ['order_index'])


    # Creating the 'media_asset' table
    op.create_table(
        'media_asset',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('file_name', sa.String(), nullable=False),
        sa.Column('mime_type', sa.String(), nullable=False),
        sa.Column('checksum', sa.String(64), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('(width IS NULL AND height IS NULL) OR (width > 0 AND height > 0)', name='ck_media_asset_dimensions_valid'),
        sa.CheckConstraint('file_size >= 0', name='ck_media_asset_file_size_nonneg'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_media_asset_checksum', 'media_asset', ['checksum'], unique=False)
    op.create_index('ix_media_asset_created_at', 'media_asset', ['created_at'], unique=False)
    op.create_index('ix_media_asset_mime_type', 'media_asset', ['mime_type'], unique=False)

    # Creating the 'person_role' table
    op.create_table(
        'person_role',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('order_index', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )
    op.create_index('ix_person_role_key', 'person_role', ['key'], unique=False)
    op.create_index('ix_person_role_order', 'person_role', ['order_index'], unique=False)

    # Creating the 'project_style' table
    op.create_table(
        'project_style',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('order_index', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('visible', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.CheckConstraint("key ~ '^[a-z0-9_]+$'", name='ck_project_style_key_slug'),
        sa.CheckConstraint('order_index >= 0', name='ck_project_style_order_nonneg'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )
    op.create_index('ix_project_style_key', 'project_style', ['key'], unique=False)
    op.create_index('ix_project_style_visible', 'project_style', ['visible'], unique=False)

    # Continue creating other tables similarly ...

def downgrade():
    op.drop_index('ix_project_style_visible', table_name='project_style')
    op.drop_index('ix_project_style_key', table_name='project_style')
    op.drop_table('project_style')
    op.drop_index('ix_person_role_order', table_name='person_role')
    op.drop_index('ix_person_role_key', table_name='person_role')
    op.drop_table('person_role')
    op.drop_index('ix_media_asset_mime_type', table_name='media_asset')
    op.drop_index('ix_media_asset_created_at', table_name='media_asset')
    op.drop_index('ix_media_asset_checksum', table_name='media_asset')
    op.drop_table('media_asset')
    op.drop_index('ix_location_city_slug', table_name='location')
    op.drop_index('ix_location_country_code', table_name='location')
    op.drop_table('location')

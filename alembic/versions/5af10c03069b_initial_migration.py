"""Initial migration for all models.

Revision ID: <your_revision_id>
Revises: None
Create Date: <timestamp>
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from uuid import uuid4

# revision identifiers, used by Alembic.
revision = '5af10c03069b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ======================================================
    # LOCATION TABLE
    # ======================================================
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

    # ======================================================
    # LOCATION_I18N TABLE
    # ======================================================
    op.create_table(
        'location_i18n',
        sa.Column('location_id', sa.UUID(), sa.ForeignKey("location.id", ondelete="CASCADE"), primary_key=True),
        sa.Column('locale', sa.Enum('en', 'ru', 'tk', name="language_enum"), primary_key=True),
        sa.Column('country', sa.String(), nullable=False),
        sa.Column('city', sa.String(), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default=sa.text("0"))
    )
    op.create_index('ix_location_i18n_locale', 'location_i18n', ['locale'], unique=False)
    op.create_index('ix_location_i18n_order_index', 'location_i18n', ['order_index'], unique=False)

    # ======================================================
    # PROJECT TYPE TABLE
    # ======================================================
    op.create_table(
        'project_type',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('key', sa.String(), nullable=False, unique=True),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column('visible', sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_project_type_key', 'project_type', ['key'])
    op.create_index('ix_project_type_visible', 'project_type', ['visible'])

    # ======================================================
    # PROJECT TABLE
    # ======================================================
    op.create_table(
        'project',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('cover_media_id', sa.UUID(), sa.ForeignKey("media_asset.id", ondelete="SET NULL")),
        sa.Column('location_id', sa.UUID(), sa.ForeignKey("location.id", ondelete="SET NULL"), nullable=True),
        sa.Column('type_id', sa.UUID(), sa.ForeignKey("project_type.id", ondelete="RESTRICT"), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('completion', sa.Integer(), nullable=True),
        sa.Column('area_m2', sa.Numeric(10, 2), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()"), onupdate=sa.text("now()")),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_project_type_loc_pub_order', 'project', ['type_id', 'location_id', 'is_published', sa.text('order_index DESC')])
    op.create_index('ix_project_loc_pub_order', 'project', ['location_id', 'is_published', sa.text('order_index DESC')])
    op.create_index('ix_project_type_pub_order', 'project', ['type_id', 'is_published', sa.text('order_index DESC')])
    op.create_index('ix_project_pub_published_at_desc', 'project', ['is_published', sa.text('published_at DESC')])

    # ======================================================
    # PROJECT_I18N TABLE
    # ======================================================
    op.create_table(
        'project_i18n',
        sa.Column('project_id', sa.UUID(), sa.ForeignKey("project.id", ondelete="CASCADE"), primary_key=True),
        sa.Column('locale', sa.Enum('en', 'ru', 'tk', name="language_enum"), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('subname', sa.String(), nullable=False),
        sa.Column('client_name', sa.String(), nullable=True),
        sa.Column('short_description', sa.Text(), nullable=True),
        sa.Column('full_description', sa.Text(), nullable=True),
        sa.Column('search_vector', sa.TSVECTOR, nullable=False),
    )
    op.create_index('ix_project_i18n_locale', 'project_i18n', ['locale'], unique=False)
    op.create_index('ix_project_i18n_search', 'project_i18n', ['search_vector'], postgresql_using='gin')

    # ======================================================
    # PROJECT_MEDIA TABLE
    # ======================================================
    op.create_table(
        'project_media',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), sa.ForeignKey("project.id", ondelete="CASCADE"), nullable=False),
        sa.Column('media_id', sa.UUID(), sa.ForeignKey("media_asset.id", ondelete="RESTRICT"), nullable=False),
        sa.Column('kind', sa.Enum('photo', 'drawing', 'hero', name="project_media_kind"), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_project_media_kind_order', 'project_media', ['project_id', 'kind', 'order_index'])
    op.create_index('ix_project_media_media', 'project_media', ['media_id'])

    # ======================================================
    # MEDIA_ASSET TABLE
    # ======================================================
    op.create_table(
        'media_asset',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('application_id', sa.UUID(), sa.ForeignKey("application.id", ondelete="CASCADE"), nullable=True),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('file_name', sa.String(), nullable=False),
        sa.Column('mime_type', sa.String(), nullable=False),
        sa.Column('checksum', sa.String(64), nullable=True, index=True),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()"), onupdate=sa.text("now()")),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_media_asset_mime_type', 'media_asset', ['mime_type'])
    op.create_index('ix_media_asset_created_at', 'media_asset', ['created_at'])

    # ======================================================
    # APPLICATION TABLE
    # ======================================================
    op.create_table(
        'applications',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('career_id', sa.UUID(), sa.ForeignKey("career.id", ondelete="CASCADE")),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('email', sa.CITEXT, nullable=False),
        sa.Column('phone_number', sa.String(), nullable=False),
        sa.Column('message', sa.String(), nullable=True),
        sa.Column('status', sa.Enum('new', 'reviewed', 'archived', name="application_status_enum"), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()"), onupdate=sa.text("now()")),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_application_created_at', 'applications', ['created_at'])
    op.create_index('ix_application_career', 'applications', ['career_id'])

    # ======================================================
    # CAREER TABLE
    # ======================================================
    op.create_table(
        'career',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()"), onupdate=sa.text("now()")),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_career_order_index', 'career', ['order_index'])
    op.create_index('ix_career_is_published', 'career', ['is_published'])

    # ======================================================
    # CONTACT MESSAGE TABLE
    # ======================================================
    op.create_table(
        'contact_message',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.CITEXT(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('new', 'reviewed', 'archived', name="contact_status_enum"), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()"), onupdate=sa.text("now()")),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_contact_message_created_at_desc', 'contact_message', ['created_at'], unique=False)
    op.create_index('ix_contact_message_status', 'contact_message', ['status'], unique=False)


def downgrade():
    op.drop_table('contact_message')
    op.drop_table('career')
    op.drop_table('applications')
    op.drop_table('media_asset')
    op.drop_table('project_media')
    op.drop_table('project_i18n')
    op.drop_table('project')
    op.drop_table('project_type')
    op.drop_table('location_i18n')
    op.drop_table('location')

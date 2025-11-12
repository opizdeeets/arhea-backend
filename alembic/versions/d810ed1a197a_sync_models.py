"""full rebuild aligned with models

Revision ID: a1b2c3d4e5f7
Revises: None
Create Date: 2025-11-11 12:00:00 UTC
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f7"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS citext;")

    # Enums: создаем заранее, а в колонках используем postgresql.ENUM(..., create_type=False)
    op.execute(
        "DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'language_enum') "
        "THEN CREATE TYPE language_enum AS ENUM ('en','ru','tk'); END IF; END $$;"
    )
    op.execute(
        "DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'application_status_enum') "
        "THEN CREATE TYPE application_status_enum AS ENUM ('new','reviewed','archived'); END IF; END $$;"
    )
    op.execute(
        "DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'contact_status_enum') "
        "THEN CREATE TYPE contact_status_enum AS ENUM ('new','reviewed','archived'); END IF; END $$;"
    )
    op.execute(
        "DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'project_media_kind') "
        "THEN CREATE TYPE project_media_kind AS ENUM ('photo','drawing','hero'); END IF; END $$;"
    )
    op.execute(
        "DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'news_media_kind') "
        "THEN CREATE TYPE news_media_kind AS ENUM ('photo','drawing','hero'); END IF; END $$;"
    )

    # =========================================
    # career
    # =========================================
    op.create_table(
        "career",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_published", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("order_index", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.CheckConstraint("order_index >= 0", name="ck_career_order_nonneg"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_career_is_published", "career", ["is_published"])
    op.create_index("ix_career_order_index", "career", ["order_index"])

    # =========================================
    # applications
    # =========================================
    op.create_table(
        "applications",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("career_id", sa.UUID(), nullable=True),
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("last_name", sa.String(), nullable=False),
        sa.Column("email", postgresql.CITEXT(), nullable=False),
        sa.Column("phone_number", sa.String(), nullable=False),
        sa.Column("message", sa.String(), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM("new", "reviewed", "archived", name="application_status_enum", create_type=False),
            server_default=sa.text("'new'::application_status_enum"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at_date", sa.Date(), server_default=sa.text("CURRENT_DATE"), nullable=False),
        sa.ForeignKeyConstraint(["career_id"], ["career.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", "career_id", "created_at_date", name="uq_application_email_per_day"),
    )
    op.create_index("ix_application_career", "applications", ["career_id"])
    op.create_index("ix_application_created_at", "applications", ["created_at"])
    op.create_index("ix_applications_status", "applications", ["status"])

    # =========================================
    # media_asset
    # =========================================
    op.create_table(
        "media_asset",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("application_id", sa.UUID(), nullable=True),
        sa.Column("file_path", sa.String(), nullable=False),
        sa.Column("file_name", sa.String(), nullable=False),
        sa.Column("mime_type", sa.String(), nullable=False),
        sa.Column("checksum", sa.String(length=64), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("file_size >= 0", name="ck_media_asset_file_size_nonneg"),
        sa.CheckConstraint(
            "(width IS NULL AND height IS NULL) OR (width > 0 AND height > 0)",
            name="ck_media_asset_dimensions_valid",
        ),
    )
    op.create_index("ix_media_asset_mime_type", "media_asset", ["mime_type"])
    op.create_index("ix_media_asset_created_at", "media_asset", ["created_at"])

    op.create_table(
        "media_asset_i18n",
        sa.Column("media_asset_id", sa.UUID(), nullable=False),
        sa.Column("locale", postgresql.ENUM("en", "ru", "tk", name="language_enum", create_type=False), nullable=False),
        sa.Column("alt_text", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["media_asset_id"], ["media_asset.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("media_asset_id", "locale"),
    )
    op.create_index("ix_media_asset_i18n_locale", "media_asset_i18n", ["locale"])

    # =========================================
    # location
    # =========================================
    op.create_table(
        "location",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("country_code", sa.String(length=2), nullable=False),
        sa.Column("city_slug", sa.String(), nullable=False),
        sa.Column("order_index", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("city_slug_lower", sa.String(), sa.Computed("lower(city_slug)"), nullable=False),
        sa.CheckConstraint("country_code ~ '^[A-Z]{2}$'", name="ck_location_country_code_iso2"),
        sa.CheckConstraint("city_slug ~ '^[a-z0-9\\- ]+$'", name="ck_location_city_slug"),
        sa.CheckConstraint("order_index >= 0", name="ck_location_order_nonneg"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("country_code", "city_slug_lower", name="uq_location_country_city_lowercase"),
    )
    op.create_index("ix_location_country_code", "location", ["country_code"])
    op.create_index("ix_location_city_slug", "location", ["city_slug"])
    op.create_index("ix_location_order_index", "location", ["order_index"])

    op.create_table(
        "location_i18n",
        sa.Column("location_id", sa.UUID(), nullable=False),
        sa.Column("locale", postgresql.ENUM("en", "ru", "tk", name="language_enum", create_type=False), nullable=False),
        sa.Column("country", sa.String(), nullable=False),
        sa.Column("city", sa.String(), nullable=False),
        sa.Column("order_index", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.ForeignKeyConstraint(["location_id"], ["location.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("location_id", "locale"),
    )
    op.create_index("ix_location_i18n_locale", "location_i18n", ["locale"])
    op.create_index("ix_location_i18n_order_index", "location_i18n", ["order_index"])

    # =========================================
    # project_type (+ i18n)
    # =========================================
    op.create_table(
        "project_type",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("order_index", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("visible", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.CheckConstraint("key ~ '^[a-z0-9_]+$'", name="ck_project_type_key_slug"),
        sa.CheckConstraint("order_index >= 0", name="ck_project_type_order_nonneg"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )
    op.create_index("ix_project_type_key", "project_type", ["key"])
    op.create_index("ix_project_type_visible", "project_type", ["visible"])

    op.create_table(
        "project_type_i18n",
        sa.Column("type_id", sa.UUID(), nullable=False),
        sa.Column("locale", postgresql.ENUM("en", "ru", "tk", name="language_enum", create_type=False), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["type_id"], ["project_type.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("type_id", "locale"),
    )
    op.create_index("ix_project_type_i18n_locale", "project_type_i18n", ["locale"])

    # =========================================
    # project_style (+ i18n, link)
    # =========================================
    op.create_table(
        "project_style",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("order_index", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("visible", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.CheckConstraint("key ~ '^[a-z0-9_]+$'", name="ck_project_style_key_slug"),
        sa.CheckConstraint("order_index >= 0", name="ck_project_style_order_nonneg"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )
    op.create_index("ix_project_style_key", "project_style", ["key"])
    op.create_index("ix_project_style_visible", "project_style", ["visible"])

    op.create_table(
        "project_style_i18n",
        sa.Column("style_id", sa.UUID(), nullable=False),
        sa.Column("locale", postgresql.ENUM("en", "ru", "tk", name="language_enum", create_type=False), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["style_id"], ["project_style.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("style_id", "locale"),
        sa.UniqueConstraint("style_id", "locale", name="uq_project_style_i18n_style_locale"),
    )
    op.create_index("ix_project_style_i18n_locale", "project_style_i18n", ["locale"])

    # =========================================
    # project (+ i18n, media)
    # =========================================
    op.create_table(
        "project",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("cover_media_id", sa.UUID(), nullable=True),
        sa.Column("location_id", sa.UUID(), nullable=True),
        sa.Column("type_id", sa.UUID(), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("completion", sa.Integer(), nullable=True),
        sa.Column("area_m2", sa.Numeric(10, 2), nullable=True),
        sa.Column("is_published", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("order_index", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("slug ~ '^[a-z0-9-]+$'", name="ck_project_slug_format"),
        sa.CheckConstraint("area_m2 IS NULL OR area_m2 >= 0", name="ck_project_area_nonneg"),
        sa.CheckConstraint("NOT is_published OR published_at IS NOT NULL", name="ck_project_published_has_date"),
        sa.CheckConstraint("year IS NULL OR (year BETWEEN 1850 AND EXTRACT(YEAR FROM now())::int + 2)", name="ck_project_year_sane"),
        sa.CheckConstraint("completion IS NULL OR (completion BETWEEN 1850 AND EXTRACT(YEAR FROM now())::int + 2)", name="ck_project_completion_sane"),
        sa.CheckConstraint("completion IS NULL OR year IS NULL OR completion >= year", name="ck_project_completion_ge_year"),
        sa.ForeignKeyConstraint(["cover_media_id"], ["media_asset.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["location_id"], ["location.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["type_id"], ["project_type.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_project_loc_pub_order", "project", ["location_id", "is_published", sa.text("order_index DESC")])
    op.create_index("ix_project_type_loc_pub_order", "project", ["type_id", "location_id", "is_published", sa.text("order_index DESC")])
    op.create_index("ix_project_type_pub_order", "project", ["type_id", "is_published", sa.text("order_index DESC")])
    op.create_index("ix_project_pub_published_at_desc", "project", ["is_published", sa.text("published_at DESC")])
    op.create_index("ix_project_slug", "project", ["slug"], unique=True)

    op.create_table(
        "project_i18n",
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("locale", postgresql.ENUM("en", "ru", "tk", name="language_enum", create_type=False), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("subname", sa.String(), nullable=False),
        sa.Column("client_name", sa.String(), nullable=True),
        sa.Column("short_description", sa.Text(), nullable=True),
        sa.Column("full_description", sa.Text(), nullable=True),
        sa.Column("search_vector", postgresql.TSVECTOR(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("project_id", "locale"),
    )
    op.create_index("ix_project_i18n_locale", "project_i18n", ["locale"])
    op.create_index("ix_project_i18n_search", "project_i18n", ["search_vector"], postgresql_using="gin")

    op.execute(
        """
CREATE OR REPLACE FUNCTION set_project_i18n_tsv() RETURNS trigger AS $$
BEGIN
  NEW.search_vector := to_tsvector('simple',
    coalesce(NEW.name,'') || ' ' ||
    coalesce(NEW.subname,'') || ' ' ||
    coalesce(NEW.client_name,'') || ' ' ||
    coalesce(NEW.short_description,'') || ' ' ||
    coalesce(NEW.full_description,'')
  );
  RETURN NEW;
END
$$ LANGUAGE plpgsql;
"""
    )
    op.execute("DROP TRIGGER IF EXISTS trg_project_i18n_tsv ON project_i18n;")
    op.execute(
        """
CREATE TRIGGER trg_project_i18n_tsv
BEFORE INSERT OR UPDATE OF name, subname, client_name, short_description, full_description
ON project_i18n
FOR EACH ROW EXECUTE FUNCTION set_project_i18n_tsv();
"""
    )

    op.create_table(
        "project_media",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("media_id", sa.UUID(), nullable=False),
        sa.Column("kind", postgresql.ENUM("photo", "drawing", "hero", name="project_media_kind", create_type=False), nullable=False),
        sa.Column("order_index", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.CheckConstraint("order_index >= 0", name="ck_project_media_order_nonneg"),
        sa.ForeignKeyConstraint(["media_id"], ["media_asset.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "media_id", "kind", name="uq_project_media_unique"),
    )
    op.create_index("ix_project_media_kind_order", "project_media", ["project_id", "kind", "order_index"])
    op.create_index("ix_project_media_media", "project_media", ["media_id"])

    # =========================================
    # people: person / person_i18n / person_role / project_person_role
    # =========================================
    op.create_table(
        "person",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("order_index", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("is_published", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("photo_media_id", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("slug ~ '^[a-z0-9-]+$'", name="ck_person_slug_format"),
        sa.CheckConstraint("order_index >= 0", name="ck_person_order_nonneg"),
        sa.ForeignKeyConstraint(["photo_media_id"], ["media_asset.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_person_slug", "person", ["slug"])
    op.create_index("ix_person_order", "person", ["order_index"])
    op.create_index("ix_person_published", "person", ["is_published"])

    op.create_table(
        "person_i18n",
        sa.Column("person_id", sa.UUID(), nullable=False),
        sa.Column("locale", postgresql.ENUM("en", "ru", "tk", name="language_enum", create_type=False), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("position_title", sa.String(), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["person_id"], ["person.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("person_id", "locale"),
        sa.UniqueConstraint("person_id", "locale", name="uq_person_i18n_person_locale"),
    )
    op.create_index("ix_person_i18n_locale", "person_i18n", ["locale"])

    op.create_table(
        "person_role",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("order_index", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )
    op.create_index("ix_person_role_key", "person_role", ["key"])
    op.create_index("ix_person_role_order", "person_role", ["order_index"])

    op.create_table(
        "person_role_i18n",
        sa.Column("person_role_id", sa.UUID(), nullable=False),
        sa.Column("locale", postgresql.ENUM("en", "ru", "tk", name="language_enum", create_type=False), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["person_role_id"], ["person_role.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("person_role_id", "locale"),
    )
    op.create_index("ix_person_role_i18n_locale", "person_role_i18n", ["locale"])

    op.create_table(
        "project_person_role",
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("person_id", sa.UUID(), nullable=False),
        sa.Column("role_id", sa.UUID(), nullable=False),
        sa.Column("order_index", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.CheckConstraint("order_index >= 0", name="ck_project_person_role_order_nonneg"),
        sa.ForeignKeyConstraint(["person_id"], ["person.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["person_role.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("project_id", "person_id", "role_id"),
    )
    op.create_index("ix_project_person_role_order", "project_person_role", ["project_id", "role_id", "order_index"])
    op.create_index("ix_project_person_role_person", "project_person_role", ["person_id"])

    # =========================================
    # project_style_link
    # =========================================
    op.create_table(
        "project_style_link",
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("style_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["style_id"], ["project_style.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("project_id", "style_id"),
    )
    op.create_index("ix_project_style_link_project", "project_style_link", ["project_id"])
    op.create_index("ix_project_style_link_style", "project_style_link", ["style_id"])
    op.create_index("ix_project_style_link_project_order", "project_style_link", ["project_id", "style_id"])

    # =========================================
    # news (+ i18n, media)
    # =========================================
    op.create_table(
        "news",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("preview", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_published", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_news_published_at", "news", ["published_at"])
    op.create_index("ix_news_is_published", "news", ["is_published"])
    op.create_index("ix_news_slug", "news", ["slug"], unique=True)

    op.create_table(
        "news_i18n",
        sa.Column("news_id", sa.UUID(), nullable=False),
        sa.Column("locale", postgresql.ENUM("en", "ru", "tk", name="language_enum", create_type=False), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("short_description", sa.Text(), nullable=False),
        sa.Column("full_description", sa.Text(), nullable=False),
        sa.Column("search_vector", postgresql.TSVECTOR(), nullable=False),
        sa.ForeignKeyConstraint(["news_id"], ["news.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("news_id", "locale"),
    )
    op.create_index("ix_news_i18n_locale", "news_i18n", ["locale"])
    op.create_index("ix_news_i18n_search", "news_i18n", ["search_vector"], postgresql_using="gin")

    op.execute(
        """
CREATE OR REPLACE FUNCTION set_news_i18n_tsv() RETURNS trigger AS $$
BEGIN
  NEW.search_vector := to_tsvector('simple',
    coalesce(NEW.title,'') || ' ' ||
    coalesce(NEW.short_description,'') || ' ' ||
    coalesce(NEW.full_description,'')
  );
  RETURN NEW;
END
$$ LANGUAGE plpgsql;
"""
    )
    op.execute("DROP TRIGGER IF EXISTS trg_news_i18n_tsv ON news_i18n;")
    op.execute(
        """
CREATE TRIGGER trg_news_i18n_tsv
BEFORE INSERT OR UPDATE OF title, short_description, full_description
ON news_i18n
FOR EACH ROW EXECUTE FUNCTION set_news_i18n_tsv();
"""
    )

    op.create_table(
        "news_media",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("news_id", sa.UUID(), nullable=False),
        sa.Column("media_id", sa.UUID(), nullable=False),
        sa.Column("kind", postgresql.ENUM("photo", "drawing", "hero", name="news_media_kind", create_type=False), nullable=False),
        sa.Column("order_index", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.ForeignKeyConstraint(["media_id"], ["media_asset.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["news_id"], ["news.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("news_id", "media_id", "kind", name="uq_news_media_unique"),
    )
    op.create_index("ix_news_media_kind_order", "news_media", ["news_id", "kind", "order_index"])

    # =========================================
    # contact_message
    # =========================================
    op.create_table(
        "contact_message",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", postgresql.CITEXT(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM("new", "reviewed", "archived", name="contact_status_enum", create_type=False),
            server_default=sa.text("'new'::contact_status_enum"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("message_hash", sa.String(length=32), nullable=False),
        sa.Column("created_at_date", sa.Date(), server_default=sa.text("CURRENT_DATE"), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("char_length(name) > 0", name="ck_contact_name_nonempty"),
        sa.CheckConstraint("char_length(message) > 0", name="ck_contact_message_nonempty"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", "message_hash", "created_at_date", name="uq_contact_message_per_day"),
    )
    op.create_index("ix_contact_message_created_at_desc", "contact_message", [sa.text("created_at DESC")])
    op.create_index("ix_contact_message_status", "contact_message", ["status"])


def downgrade() -> None:
    # Drop triggers and functions first
    op.execute("DROP TRIGGER IF EXISTS trg_project_i18n_tsv ON project_i18n;")
    op.execute("DROP FUNCTION IF EXISTS set_project_i18n_tsv();")
    op.execute("DROP TRIGGER IF EXISTS trg_news_i18n_tsv ON news_i18n;")
    op.execute("DROP FUNCTION IF EXISTS set_news_i18n_tsv();")

    # Drop tables in reverse order
    op.drop_index("ix_contact_message_status", table_name="contact_message")
    op.drop_index("ix_contact_message_created_at_desc", table_name="contact_message")
    op.drop_table("contact_message")

    op.drop_index("ix_news_media_kind_order", table_name="news_media")
    op.drop_table("news_media")

    op.drop_index("ix_news_i18n_search", table_name="news_i18n", postgresql_using="gin")
    op.drop_index("ix_news_i18n_locale", table_name="news_i18n")
    op.drop_table("news_i18n")

    op.drop_index("ix_news_slug", table_name="news")
    op.drop_index("ix_news_is_published", table_name="news")
    op.drop_index("ix_news_published_at", table_name="news")
    op.drop_table("news")

    op.drop_index("ix_project_style_link_project_order", table_name="project_style_link")
    op.drop_index("ix_project_style_link_style", table_name="project_style_link")
    op.drop_index("ix_project_style_link_project", table_name="project_style_link")
    op.drop_table("project_style_link")

    op.drop_index("ix_project_person_role_person", table_name="project_person_role")
    op.drop_index("ix_project_person_role_order", table_name="project_person_role")
    op.drop_table("project_person_role")

    op.drop_index("ix_person_role_i18n_locale", table_name="person_role_i18n")
    op.drop_table("person_role_i18n")

    op.drop_index("ix_person_role_order", table_name="person_role")
    op.drop_index("ix_person_role_key", table_name="person_role")
    op.drop_table("person_role")

    op.drop_index("ix_person_i18n_locale", table_name="person_i18n")
    op.drop_table("person_i18n")

    op.drop_index("ix_person_published", table_name="person")
    op.drop_index("ix_person_order", table_name="person")
    op.drop_index("ix_person_slug", table_name="person")
    op.drop_table("person")

    op.drop_index("ix_project_media_media", table_name="project_media")
    op.drop_index("ix_project_media_kind_order", table_name="project_media")
    op.drop_table("project_media")

    op.drop_index("ix_project_i18n_search", table_name="project_i18n", postgresql_using="gin")
    op.drop_index("ix_project_i18n_locale", table_name="project_i18n")
    op.drop_table("project_i18n")

    op.drop_index("ix_project_slug", table_name="project")
    op.drop_index("ix_project_pub_published_at_desc", table_name="project")
    op.drop_index("ix_project_type_pub_order", table_name="project")
    op.drop_index("ix_project_type_loc_pub_order", table_name="project")
    op.drop_index("ix_project_loc_pub_order", table_name="project")
    op.drop_table("project")

    op.drop_index("ix_project_style_i18n_locale", table_name="project_style_i18n")
    op.drop_table("project_style_i18n")

    op.drop_index("ix_project_style_visible", table_name="project_style")
    op.drop_index("ix_project_style_key", table_name="project_style")
    op.drop_table("project_style")

    op.drop_index("ix_project_type_i18n_locale", table_name="project_type_i18n")
    op.drop_table("project_type_i18n")

    op.drop_index("ix_project_type_visible", table_name="project_type")
    op.drop_index("ix_project_type_key", table_name="project_type")
    op.drop_table("project_type")

    op.drop_index("ix_location_i18n_order_index", table_name="location_i18n")
    op.drop_index("ix_location_i18n_locale", table_name="location_i18n")
    op.drop_table("location_i18n")

    op.drop_index("ix_location_order_index", table_name="location")
    op.drop_index("ix_location_city_slug", table_name="location")
    op.drop_index("ix_location_country_code", table_name="location")
    op.drop_table("location")

    op.drop_index("ix_media_asset_i18n_locale", table_name="media_asset_i18n")
    op.drop_table("media_asset_i18n")

    op.drop_index("ix_media_asset_created_at", table_name="media_asset")
    op.drop_index("ix_media_asset_mime_type", table_name="media_asset")
    op.drop_table("media_asset")

    op.drop_index("ix_applications_status", table_name="applications")
    op.drop_index("ix_application_created_at", table_name="applications")
    op.drop_index("ix_application_career", table_name="applications")
    op.drop_table("applications")

    op.drop_index("ix_career_order_index", table_name="career")
    op.drop_index("ix_career_is_published", table_name="career")
    op.drop_table("career")

    # Опционально можно удалить типы (если это реально нужно для очистки)
    # op.execute("DO $$ BEGIN IF to_regtype('news_media_kind') IS NOT NULL THEN DROP TYPE news_media_kind; END IF; END $$;")
    # op.execute("DO $$ BEGIN IF to_regtype('project_media_kind') IS NOT NULL THEN DROP TYPE project_media_kind; END IF; END $$;")
    # op.execute("DO $$ BEGIN IF to_regtype('contact_status_enum') IS NOT NULL THEN DROP TYPE contact_status_enum; END IF; END $$;")
    # op.execute("DO $$ BEGIN IF to_regtype('application_status_enum') IS NOT NULL THEN DROP TYPE application_status_enum; END IF; END $$;")
    # op.execute("DO $$ BEGIN IF to_regtype('language_enum') IS NOT NULL THEN DROP TYPE language_enum; END IF; END $$;")

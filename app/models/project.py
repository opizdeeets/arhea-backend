from __future__ import annotations

import enum
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import (
    Column, String, Text, DateTime, ForeignKey, Integer, Boolean, Numeric,
    CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum as SQLEnum
from app.models.taxonomy import LanguageEnumType
from app.core.db import Base


class ProjectMediaKind(enum.Enum):
    PHOTO = "photo"
    DRAWING = "drawing"
    HERO = "hero"

ProjectMediaKindType = SQLEnum(ProjectMediaKind, name="project_media_kind", native_enum=True)

# ======================================================
#                     PROJECT TYPE
# ======================================================
class ProjectType(Base):
    __tablename__ = "project_type"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    key = Column(String, nullable=False, unique=True)
    order_index = Column(Integer, nullable=False, server_default=sa.text("0"))
    visible = Column(Boolean, nullable=False, server_default=sa.text("true"))

    projects = relationship("Project", back_populates="project_type")

    __table_args__ = (
        Index("ix_project_type_key", "key"),
        Index("ix_project_type_visible", "visible"),
        CheckConstraint("order_index >= 0", name="ck_project_type_order_nonneg"),  
        CheckConstraint("key ~ '^[a-z0-9_]+$'", name="ck_project_type_key_slug"),  

    )


class ProjectTypeI18n(Base):
    __tablename__ = "project_type_i18n"

    type_id = Column(UUID(as_uuid=True), ForeignKey("project_type.id", ondelete="CASCADE"), primary_key=True)
    locale = Column(LanguageEnumType, primary_key=True)
    title = Column(String, nullable=False)

    __table_args__ = (
        Index("ix_project_type_i18n_locale", "locale"),
    )


# ======================================================
#                     PROJECT STYLE
# ======================================================
class ProjectStyle(Base):
    __tablename__ = "project_style"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    key = Column(String, nullable=False, unique=True)
    order_index = Column(Integer, nullable=False, server_default=sa.text("0"))
    visible = Column(Boolean, nullable=False, server_default=sa.text("true"))

    project_links = relationship("ProjectStyleLink", back_populates="style", cascade="all, delete-orphan", lazy="selectin")

    __table_args__ = (
        Index("ix_project_style_key", "key"),
        Index("ix_project_style_visible", "visible"),
        CheckConstraint("order_index >= 0", name="ck_project_style_order_nonneg"),
        CheckConstraint("key ~ '^[a-z0-9_]+$'", name="ck_project_style_key_slug"),
    )


class ProjectStyleI18n(Base):
    __tablename__ = "project_style_i18n"

    style_id = Column(UUID(as_uuid=True), ForeignKey("project_style.id", ondelete="CASCADE"), primary_key=True)
    locale = Column(LanguageEnumType, primary_key=True)
    title = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint("style_id", "locale", name="uq_project_style_i18n_style_locale"),
        Index("ix_project_style_i18n_locale", "locale"),
    )


class ProjectStyleLink(Base):
    __tablename__ = "project_style_link"

    project_id = Column(UUID(as_uuid=True), ForeignKey("project.id", ondelete="CASCADE"), primary_key=True)
    style_id = Column(UUID(as_uuid=True), ForeignKey("project_style.id", ondelete="RESTRICT"), primary_key=True)

    project = relationship("Project", back_populates="style_links")
    style = relationship("ProjectStyle", back_populates="project_links")

    __table_args__ = (
        Index("ix_project_style_link_project", "project_id"),
        Index("ix_project_style_link_style", "style_id"),
        Index("ix_project_style_link_project_order", "project_id", "style_id"),
    )


# ======================================================
#                        PROJECT
# ======================================================
class Project(Base):
    """
    Языконезависимая часть проекта.
    """
    __tablename__ = "project"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    slug = Column(String, nullable=False, unique=True, index=True)

    cover_media_id = Column(UUID(as_uuid=True), ForeignKey("media_asset.id", ondelete="SET NULL"))
    location_id = Column(UUID(as_uuid=True), ForeignKey("location.id", ondelete="SET NULL"), nullable=True)
    type_id = Column(UUID(as_uuid=True), ForeignKey("project_type.id", ondelete="RESTRICT"), nullable=True)

    year = Column(Integer, nullable=True)            # старт или референсный год
    completion = Column(Integer, nullable=True)      # год завершения (если есть)
    area_m2 = Column(Numeric(10, 2), nullable=True)

    is_published = Column(Boolean, nullable=False, server_default=sa.text("false"))
    published_at = Column(DateTime(timezone=True), nullable=True)
    order_index = Column(Integer, nullable=False, server_default=sa.text("0"))

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=sa.text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=sa.text("now()"), onupdate=sa.text("now()"))

    # relations
    cover = relationship("MediaAsset", foreign_keys=[cover_media_id])
    location = relationship("Location", foreign_keys=[location_id])
    project_type = relationship("ProjectType", foreign_keys=[type_id], back_populates="projects")

    translations = relationship("ProjectI18n", back_populates="project", cascade="all, delete-orphan", lazy="selectin")
    style_links = relationship("ProjectStyleLink", back_populates="project", cascade="all, delete-orphan", lazy="selectin")
    styles = relationship("ProjectStyle", secondary="project_style_link", viewonly=True, lazy="selectin")
    person_roles = relationship("ProjectPersonRole", back_populates="project", cascade="all, delete-orphan", lazy="selectin")
    media = relationship("ProjectMedia", back_populates="project", cascade="all, delete-orphan", lazy="selectin")

    __table_args__ = (
    CheckConstraint("slug ~ '^[a-z0-9-]+$'", name="ck_project_slug_format"),

    # Индексы под фильтры и сортировки
    Index("ix_project_type_loc_pub_order",
          "type_id", "location_id", "is_published", sa.text("order_index DESC")),
    Index("ix_project_loc_pub_order",
          "location_id", "is_published", sa.text("order_index DESC")),
    Index("ix_project_type_pub_order",
          "type_id", "is_published", sa.text("order_index DESC")),
    Index("ix_project_pub_published_at_desc",
          "is_published", sa.text("published_at DESC")),

    # Инварианты
    CheckConstraint("area_m2 IS NULL OR area_m2 >= 0", name="ck_project_area_nonneg"),
    CheckConstraint("NOT is_published OR published_at IS NOT NULL",
                    name="ck_project_published_has_date"),
    CheckConstraint("year IS NULL OR (year BETWEEN 1850 AND EXTRACT(YEAR FROM now())::int + 2)",
                    name="ck_project_year_sane"),
    CheckConstraint("completion IS NULL OR (completion BETWEEN 1850 AND EXTRACT(YEAR FROM now())::int + 2)",
                    name="ck_project_completion_sane"),
    CheckConstraint("completion IS NULL OR year IS NULL OR completion >= year",
                    name="ck_project_completion_ge_year"),
)


class ProjectI18n(Base):
    """
    Переводы проекта: по одной строке на локаль.
    Храним все текстовые поля + вектор поиска.
    """
    __tablename__ = "project_i18n"

    project_id = Column(UUID(as_uuid=True), ForeignKey("project.id", ondelete="CASCADE"), primary_key=True)
    locale = Column(LanguageEnumType, primary_key=True)

    name = Column(String, nullable=False)
    subname = Column(String, nullable=False)
    client_name = Column(String, nullable=True)
    short_description = Column(Text, nullable=True)
    full_description = Column(Text, nullable=True)

    search_vector = Column(TSVECTOR, nullable=False)
    nullable=False
   
    project = relationship("Project", back_populates="translations")

    __table_args__ = (
        Index("ix_project_i18n_locale", "locale"),
        Index("ix_project_i18n_search", "search_vector", postgresql_using="gin"),
    )


# ======================================================
#                       PROJECT MEDIA
# ======================================================
class ProjectMedia(Base):
    __tablename__ = "project_media"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("project.id", ondelete="CASCADE"), nullable=False)
    media_id = Column(UUID(as_uuid=True), ForeignKey("media_asset.id", ondelete="RESTRICT"), nullable=False)
    kind = Column(ProjectMediaKindType, nullable=False)
    order_index = Column(Integer, nullable=False, server_default=sa.text("0"))

    # правильно: связь на Project и на MediaAsset
    project = relationship("Project", back_populates="media")
    media = relationship("MediaAsset", back_populates="project_media")

    __table_args__ = (
    CheckConstraint("order_index >= 0", name="ck_project_media_order_nonneg"),
    UniqueConstraint("project_id", "media_id", "kind", name="uq_project_media_unique"),
    Index("ix_project_media_kind_order", "project_id", "kind", "order_index"),
    Index("ix_project_media_media", "media_id"),
)

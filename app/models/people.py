from __future__ import annotations

import enum
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import (
    Column, String, Text, DateTime, ForeignKey, Integer, Boolean, Numeric,
    CheckConstraint, UniqueConstraint, Index, Computed
)
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum as SQLEnum
from app.models.taxonomy import LanguageEnumType
from app.core.db import Base



# ======================================================
#                     PERSON / ROLES
# ======================================================
class Person(Base):
    __tablename__ = "person"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    slug = Column(String, nullable=False, unique=True)
    order_index = Column(Integer, nullable=False, server_default=sa.text("0"))
    is_published = Column(Boolean, nullable=False, server_default=sa.text("true"))
    photo_media_id = Column(UUID(as_uuid=True), ForeignKey("media_asset.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=sa.text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=sa.text("now()"), onupdate=sa.text("now()"))

    photo = relationship("MediaAsset")
    project_roles = relationship("ProjectPersonRole", back_populates="person", cascade="all, delete-orphan", lazy="selectin")
    translations = relationship("PersonI18n", back_populates="person", cascade="all, delete-orphan", lazy="selectin")

    __table_args__ = (
        Index("ix_person_slug", "slug"),
        Index("ix_person_order", "order_index"),
        Index("ix_person_published", "is_published"),
        CheckConstraint("order_index >= 0", name="ck_person_order_nonneg"),
        CheckConstraint("slug ~ '^[a-z0-9-]+$'", name="ck_person_slug_format"),

    )


class PersonI18n(Base):
    __tablename__ = "person_i18n"

    person_id = Column(UUID(as_uuid=True), ForeignKey("person.id", ondelete="CASCADE"), primary_key=True)
    locale = Column(LanguageEnumType, primary_key=True)

    full_name = Column(String, nullable=False)
    position_title = Column(String, nullable=True)
    bio = Column(Text, nullable=True)

    person = relationship("Person", back_populates="translations")

    __table_args__ = (
        UniqueConstraint("person_id", "locale", name="uq_person_i18n_person_locale"),
        Index("ix_person_i18n_locale", "locale"),
    )


class PersonRole(Base):
    __tablename__ = "person_role"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    key = Column(String, nullable=False, unique=True)  # 'architect', 'lead_designer', ...
    order_index = Column(Integer, nullable=False, server_default=sa.text("0"))

    project_links = relationship("ProjectPersonRole", back_populates="role", cascade="all, delete-orphan")
    translations = relationship("PersonRoleI18n", back_populates="role", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_person_role_key", "key"),
        Index("ix_person_role_order", "order_index"),
    )


class PersonRoleI18n(Base):
    __tablename__ = "person_role_i18n"

    person_role_id = Column(UUID(as_uuid=True), ForeignKey("person_role.id", ondelete="CASCADE"), primary_key=True)
    locale = Column(LanguageEnumType, primary_key=True)
    title = Column(String, nullable=False)

    role = relationship("PersonRole", back_populates="translations")

    __table_args__ = (
        Index("ix_person_role_i18n_locale", "locale"),
    )


class ProjectPersonRole(Base):
    __tablename__ = "project_person_role"

    project_id = Column(UUID(as_uuid=True), ForeignKey("project.id", ondelete="CASCADE"), primary_key=True)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("person_role.id", ondelete="RESTRICT"), primary_key=True)
    order_index = Column(Integer, nullable=False, server_default=sa.text("0"))

    project = relationship("Project", back_populates="person_roles")
    person = relationship("Person", back_populates="project_roles")
    role = relationship("PersonRole", back_populates="project_links")

    __table_args__ = (
        Index("ix_project_person_role_order", "project_id", "role_id", "order_index"),
        CheckConstraint("order_index >= 0", name="ck_project_person_role_order_nonneg"),
        Index("ix_project_person_role_person", "person_id"),

    )


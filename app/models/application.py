from __future__ import annotations

import enum
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import (
    Column, String, Text, DateTime, ForeignKey, Integer, Boolean, Numeric,
    CheckConstraint, UniqueConstraint, Index, Computed, func,
)
from sqlalchemy.dialects.postgresql import UUID, CITEXT
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum as SQLEnum
from app.models.taxonomy import LanguageEnumType
from app.core.db import Base


# ======================================================
#                     Application
# ======================================================

class ApplicationStatus(enum.Enum):
    NEW = "new"
    REVIEWED = "reviewed"
    ARCHIVED = "archived"

ApplicationStatusType = SQLEnum(ApplicationStatus, name="application_status_enum", native_enum=True)

class Application(Base):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    career_id = Column(UUID(as_uuid=True), ForeignKey("career.id", ondelete="CASCADE"))
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)    
    email = Column(CITEXT   , nullable=False)
    phone_number = Column(String, nullable=False)
    message = Column(String, nullable=True)
    status = Column(ApplicationStatusType, nullable=False, index=True, server_default=sa.text("'new'::application_status_enum"))

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=sa.text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=sa.text("now()"), onupdate=sa.text("now()"))

    files = relationship("MediaAsset", back_populates="applications")
    career = relationship("Career", back_populates="applications")


    __table_args__ = (
    UniqueConstraint("email", "career_id", sa.text("created_at::date"), name="uq_application_email_per_day"),
    Index("ix_application_created_at", "created_at"),
    Index("ix_application_career", "career_id"),
)

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
#                     CAREER
# ======================================================
class Career(Base):
    __tablename__ = "career"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=sa.text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=sa.text("now()"), onupdate=sa.text("now()"))
    is_published = Column(Boolean, nullable=False, server_default=sa.text("false"))
    order_index = Column(Integer, nullable=False, server_default=sa.text("0"))
    

    applications = relationship("Application", back_populates="career")

    __table_args__ = (
        Index("ix_career_order_index", "order_index"),
        Index("ix_career_is_published", "is_published"),
        CheckConstraint("order_index >= 0", name="ck_career_order_nonneg"),
    )



class CareerI18n(Base):
    __tablename__ = "career_i18n"

    career_id = Column(UUID(as_uuid=True), ForeignKey("career.id", ondelete="CASCADE"), primary_key=True)
    locale = Column(LanguageEnumType, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    __table_args__ = (
        Index("ix_career_i18n_locale", "locale"),
    )

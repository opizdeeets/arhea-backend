from __future__ import annotations

import enum
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import (
    Column, String, Text, DateTime, ForeignKey, Integer, Boolean, Numeric,
    CheckConstraint, UniqueConstraint, Index, Computed, func
)
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum as SQLEnum
from app.models.taxonomy import LanguageEnumType
from app.core.db import Base



# ======================================================
#                     JobApplication
# ======================================================

class Application(Base):
    __tablename__ = "application"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    career_id = Column(UUID(as_uuid=True), ForeignKey("career.id"))
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)    
    email = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    message = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=sa.text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=sa.text("now()"), onupdate=sa.text("now()"))

    files = relationship("MediaAsset", back_populates="application")
    application = relationship("Career", back_populates="application")
from __future__ import annotations

from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import (
    Column, String, DateTime, ForeignKey, Integer, 
    CheckConstraint, Index
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.taxonomy import LanguageEnumType
from app.core.db import Base

# ======================================================
#                     MEDIA ASSET
# ======================================================
class MediaAsset(Base):
    __tablename__ = "media_asset"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"), nullable=True)
    file_path = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    checksum = Column(String(64), nullable=True, index=True)
    file_size = Column(Integer, nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=sa.text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=sa.text("now()"), onupdate=sa.text("now()"))
    project_media = relationship("ProjectMedia", back_populates="media", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="files")

    __table_args__ = (
        Index("ix_media_asset_mime_type", "mime_type"),
        CheckConstraint("file_size >= 0", name="ck_media_asset_file_size_nonneg"),
        CheckConstraint(
            "(width IS NULL AND height IS NULL) OR (width > 0 AND height > 0)",
            name="ck_media_asset_dimensions_valid"
        ),
        Index("ix_media_asset_created_at", "created_at"),
    )


class MediaAssetI18n(Base):
    __tablename__ = "media_asset_i18n"

    asset_id = Column(UUID(as_uuid=True), ForeignKey("media_asset.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    locale = Column(LanguageEnumType, primary_key=True)
    alt_text = Column(String, nullable=True)

    __table_args__ = (
    Index("ix_media_asset_i18n_locale", "locale"),
)
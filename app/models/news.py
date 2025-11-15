from __future__ import annotations

import enum
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import (
    Column, String, Text, DateTime, ForeignKey, Integer, Boolean, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum as SQLEnum
from app.models.taxonomy import LanguageEnumType
from app.core.db import Base


# ======================================================
#                         News
# ======================================================

class NewsMediaKind(enum.Enum):
    PHOTO = "photo"
    DRAWING = "drawing"
    HERO = "hero"

NewsMediaKindType = SQLEnum(
    NewsMediaKind,
    values_callable=lambda enum_cls: [m.value for m in enum_cls],  # храним 'photo'|'drawing'|'hero'
    validate_strings=True,
    name="news_media_kind",
    native_enum=True,
)
class News(Base):
    __tablename__ = "news"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    slug = Column(String, nullable=False, unique=True, index=True)  
    preview = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=sa.text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=sa.text("now()"), onupdate=sa.text("now()"))
    is_published = Column(Boolean, nullable=False, server_default=sa.text("false"))
    published_at = Column(DateTime(timezone=True), nullable=True)

    translations = relationship("NewsI18n", back_populates="news")
    media_items = relationship("NewsMedia", back_populates="news", cascade="all, delete-orphan", lazy="selectin")

    __table_args__ = (
        Index("ix_news_published_at", "published_at"),
        Index("ix_news_is_published", "is_published"),
    )


class NewsI18n(Base):
    __tablename__ = "news_i18n" 

    news_id = Column(UUID(as_uuid=True), ForeignKey("news.id", ondelete="CASCADE"), primary_key=True)
    locale = Column(LanguageEnumType, primary_key=True)
    title = Column(String, nullable=False)
    short_description = Column(Text, nullable=False)
    full_description = Column(Text, nullable=False)
    search_vector = Column(TSVECTOR, nullable=False)

    news = relationship("News", back_populates="translations")

    __table_args__ = (
        Index("ix_news_i18n_locale", "locale"),
        Index("ix_news_i18n_search", "search_vector", postgresql_using="gin"),
    )


class NewsMedia(Base):
    __tablename__ = "news_media"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    news_id = Column(UUID(as_uuid=True), ForeignKey("news.id", ondelete="CASCADE"), nullable=False)
    media_id = Column(UUID(as_uuid=True), ForeignKey("media_asset.id", ondelete="RESTRICT"), nullable=False)
    kind = Column(NewsMediaKindType, nullable=False)
    order_index = Column(Integer, nullable=False, server_default=sa.text("0"))

    news = relationship("News", back_populates="media_items")
    media = relationship("MediaAsset")

    __table_args__ = (
        Index("ix_news_media_kind_order", "news_id", "kind", "order_index"),
        UniqueConstraint("news_id", "media_id", "kind", name="uq_news_media_unique"),  
    )

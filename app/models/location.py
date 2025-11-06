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
#                     LOCATION
# ======================================================
class Location(Base):
    __tablename__ = "location"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    country_code = Column(String(2), nullable=False)   # ISO-3166-1 alpha-2: 'FR', 'RU', 'TM'
    city_slug = Column(String, nullable=True)          # machine-readable: 'paris', 'moscow'
    order_index = Column(Integer, nullable=False, server_default=sa.text("0"))

    __table_args__ = (
    Index("ix_location_country_code", "country_code"),
    Index("ix_location_city_slug", "city_slug"),
    Index("ix_location_order_index", "order_index"),
    UniqueConstraint("country_code", "LOWER(city_slug)", name="uq_location_country_city_lowercase"),
    CheckConstraint("country_code ~ '^[A-Z]{2}$'", name="ck_location_country_code_iso2"),
    CheckConstraint("city_slug ~ '^[a-z0-9a-zÀ-ÿ\\- ]+$'", name="ck_location_city_slug"),
    CheckConstraint("order_index >= 0", name="ck_location_order_nonneg"),
)


class LocationI18n(Base):
    __tablename__ = "location_i18n"

    location_id = Column(UUID(as_uuid=True), ForeignKey("location.id", ondelete="CASCADE"), primary_key=True)
    locale = Column(LanguageEnumType, primary_key=True)

    country = Column(String, nullable=False)
    city = Column(String, nullable=False)

    __table_args__ = (
    Index("ix_location_i18n_locale", "locale"),
    Index("ix_location_order_index", "order_index"),
)

        
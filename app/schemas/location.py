from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from app.models.taxonomy import LanguageEnum


# ---------------------- i18n ----------------------


class LocationI18nBase(BaseModel):
    locale: LanguageEnum
    country: str
    city: str
    order_index: int | None = None


class LocationI18nCreate(LocationI18nBase):
    pass


class LocationI18nRead(LocationI18nBase):
    location_id: UUID

    model_config = ConfigDict(from_attributes=True)


# ---------------------- basic ----------------------


class LocationBase(BaseModel):
    country_code: str   # 'FR', 'RU', 'TM'
    city_slug: str      # 'paris', 'moscow'
    order_index: int | None = None


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    country_code: str | None = None
    city_slug: str | None = None
    order_index: int | None = None


class LocationRead(LocationBase):
    id: UUID
    translations: list[LocationI18nRead] = []

    model_config = ConfigDict(from_attributes=True)
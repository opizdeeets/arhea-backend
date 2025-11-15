from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.taxonomy import LanguageEnum
from uuid import UUID


# ======================================================
#                         i18n
# ======================================================

class CareerI18nBase(BaseModel):
    locale: LanguageEnum
    title: str | None = None
    description: str | None = None


class CareerI18nCreate(CareerI18nBase):
    locale: LanguageEnum = LanguageEnum.EN
    title: str
    description: str


class CareerI18nUpdate(CareerI18nBase):
    pass

class CareerI18nRead(CareerI18nBase):
    career_id: UUID # явно будем указывать родительский айди, т.к у i18n таблиц нет своего id, из-за чего бек может упасть.
    model_config = ConfigDict(from_attributes=True)



# ======================================================
#                         basic
# ======================================================

class CareerBase(BaseModel):
    order_index: int | None = None


class CareerCreate(CareerBase):
    translations: list[CareerI18nCreate]
    is_published: bool = False


class CareerUpdate(BaseModel):
    order_index: int | None = None
    is_published: bool | None = None


class CareerRead(CareerBase):
    id: UUID
    is_published: bool
    created_at: datetime
    updated_at: datetime | None = None
    translations: list[CareerI18nRead]
    model_config = ConfigDict(from_attributes=True)


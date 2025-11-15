from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.taxonomy import LanguageEnum
from uuid import UUID


# ======================================================
#                         i18n
# ======================================================

class NewsI18nBase(BaseModel):
    locale: LanguageEnum
    title: str
    short_description: str
    full_description: str


class NewsI18nCreate(NewsI18nBase):
    locale: LanguageEnum = LanguageEnum.EN


class NewsI18nRead(NewsI18nBase):
    news_id: UUID
    model_config = ConfigDict(from_attributes=True)




# ======================================================
#                         basic
# ======================================================

class NewsBase(BaseModel):
    slug: str
    is_published: bool = False
    published_at: datetime | None = None
    preview: str | None = None  

class NewsCreate(NewsBase):
    translations: list[NewsI18nCreate]


class NewsUpdate(BaseModel):
    slug: str | None = None
    is_published: bool | None = None
    published_at: datetime | None = None
    preview: str | None = None


class NewsRead(NewsBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None     
    translations: list[NewsI18nRead]

    model_config = ConfigDict(from_attributes=True)


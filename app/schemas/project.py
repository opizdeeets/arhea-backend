from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from app.models.taxonomy import LanguageEnum
from app.models.project import ProjectMediaKind




# ======================================================
#                        PROJECT
# ======================================================

class ProjectI18nBase(BaseModel):
    locale: LanguageEnum
    name: str
    subname: str
    client_name: str | None = None
    short_description: str | None = None
    full_description: str | None = None

class ProjectI18nCreate(ProjectI18nBase):
    pass

class ProjectI18nRead(ProjectI18nBase):
    project_id: UUID
    model_config = ConfigDict(from_attributes=True)
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
#                        i18n
#                        ----
#                        basic
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class ProjectBase(BaseModel):
    slug: str
    cover_media_id: UUID | None = None
    location_id: UUID | None = None
    type_id: UUID | None = None

    year: int | None = None          # старт/реф. год
    completion: int | None = None    # год завершения
    area_m2: float | None = None     # можешь Decimal, но для схем чаще float

    is_published: bool = False
    published_at: datetime | None = None
    order_index: int = 0

class ProjectCreate(ProjectBase):
    translations: list[ProjectI18nCreate]

class ProjectUpdate(BaseModel):
    slug: str | None = None
    cover_media_id: UUID | None = None
    location_id: UUID | None = None
    type_id: UUID | None = None

    year: int | None = None
    completion: int | None = None
    area_m2: float | None = None

    is_published: bool | None = None
    published_at: datetime | None = None
    order_index: int | None = None

class ProjectRead(ProjectBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None

    translations: list[ProjectI18nRead]

    model_config = ConfigDict(from_attributes=True)

# ======================================================
#                     PROJECT TYPE
# ======================================================

class ProjectTypeI18nRead(BaseModel):
    type_id: UUID
    locale: LanguageEnum
    title: str
    model_config = ConfigDict(from_attributes=True)
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
#                        i18n
#                        ----
#                        basic
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class ProjectTypeBase(BaseModel):
    key: str
    order_index: int | None = None
    visible: bool = True

class ProjectTypeCreate(ProjectTypeBase):
    pass

class ProjectTypeRead(ProjectTypeBase):
    id: UUID
    translations: list[ProjectTypeI18nRead]
    model_config = ConfigDict(from_attributes=True)


# ======================================================
#                     PROJECT STYLE
# ======================================================

class ProjectStyleI18nRead(BaseModel):
    style_id: UUID
    locale: LanguageEnum
    title: str

    model_config = ConfigDict(from_attributes=True)
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
#                        i18n
#                        ----
#                        basic
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class ProjectStyleBase(BaseModel):
    key: str
    order_index: int | None = None
    visible: bool = True

class ProjectStyleCreate(ProjectStyleBase):
    pass

class ProjectStyleRead(ProjectStyleBase):
    id: UUID
    translations: list[ProjectStyleI18nRead]

    model_config = ConfigDict(from_attributes=True)


# ======================================================
#                    PROJECT MEDIA
# ======================================================
class ProjectMediaBase(BaseModel):
    project_id: UUID
    media_id: UUID
    kind: ProjectMediaKind
    order_index: int | None = None


class ProjectMediaCreate(ProjectMediaBase):
    # Для создания нам нужны все поля из Base.
    # id сгенерирует БД.
    pass


class ProjectMediaUpdate(BaseModel):
    # Частичное обновление
    kind: ProjectMediaKind | None = None
    order_index: int | None = None


class ProjectMediaRead(ProjectMediaBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)

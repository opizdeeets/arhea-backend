# ======================================================
#                        PEOPLE
# ======================================================

from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.taxonomy import LanguageEnum  


# ---------------------- Person i18n ----------------------


class PersonI18nBase(BaseModel):
    locale: LanguageEnum
    full_name: str
    position_title: str | None = None
    bio: str | None = None


class PersonI18nCreate(PersonI18nBase):
    pass


class PersonI18nRead(PersonI18nBase):
    person_id: UUID

    model_config = ConfigDict(from_attributes=True)


# ---------------------- Person ----------------------


class PersonBase(BaseModel):
    slug: str
    order_index: int | None = None
    is_published: bool = True
    photo_media_id: UUID | None = None


class PersonCreate(PersonBase):
    translations: list[PersonI18nCreate]


class PersonUpdate(BaseModel):
    slug: str | None = None
    order_index: int | None = None
    is_published: bool | None = None
    photo_media_id: UUID | None = None


class PersonRead(PersonBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None
    translations: list[PersonI18nRead]

    model_config = ConfigDict(from_attributes=True)


# ---------------------- PersonRole i18n ----------------------


class PersonRoleI18nBase(BaseModel):
    locale: LanguageEnum
    title: str


class PersonRoleI18nCreate(PersonRoleI18nBase):
    pass


class PersonRoleI18nRead(PersonRoleI18nBase):
    person_role_id: UUID

    model_config = ConfigDict(from_attributes=True)


# ---------------------- PersonRole ----------------------


class PersonRoleBase(BaseModel):
    key: str        # 'architect', 'lead_designer', ...
    order_index: int | None = None


class PersonRoleCreate(PersonRoleBase):
    translations: list[PersonRoleI18nCreate]


class PersonRoleUpdate(BaseModel):
    key: str | None = None
    order_index: int | None = None


class PersonRoleRead(PersonRoleBase):
    id: UUID
    translations: list[PersonRoleI18nRead]

    model_config = ConfigDict(from_attributes=True)


# ---------------------- ProjectPersonRole (link) ----------------------


class ProjectPersonRoleBase(BaseModel):
    project_id: UUID
    person_id: UUID
    role_id: UUID
    order_index: int | None = None


class ProjectPersonRoleCreate(ProjectPersonRoleBase):
    pass


class ProjectPersonRoleRead(ProjectPersonRoleBase):
    model_config = ConfigDict(from_attributes=True)

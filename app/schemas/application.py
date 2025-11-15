from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.taxonomy import LanguageEnum
from uuid import UUID
from app.models.application import ApplicationStatus

class ApplicationBase(BaseModel):
    career_id: UUID | None = None
    first_name: str
    last_name: str
    email: str
    phone_number: str
    message: str | None = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    status: ApplicationStatus | None = None
    message: str | None = None


class ApplicationRead(ApplicationBase):
    id: UUID
    status: ApplicationStatus
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from app.models.contact import ContactStatus



class ContactMessageBase(BaseModel):
    name: str
    email: str
    message: str
    source: str



class ContactMessageCreate(ContactMessageBase):
    pass

class ContactMessageUpdate(BaseModel):
    status: ContactStatus | None = None



class ContactMessageRead(ContactMessageBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None
    processed_at: datetime | None = None
    status: ContactStatus
    model_config = ConfigDict(from_attributes=True)


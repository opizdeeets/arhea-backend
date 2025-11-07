from __future__ import annotations

import enum
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import (
    Column, String, Text, DateTime,
    CheckConstraint, UniqueConstraint, Index, Date
)
from sqlalchemy.dialects.postgresql import UUID, CITEXT
from sqlalchemy.types import Enum as SQLEnum
from app.models.application import ApplicationStatusType
from app.models.taxonomy import LanguageEnumType
from app.core.db import Base
import hashlib
from datetime import datetime, timezone

from sqlalchemy.orm import validates
from sqlalchemy import event

# ======================================================
#                     ContactMessage
# ======================================================

class ContactStatus(enum.Enum):

    NEW = "new"
    REVIEWED = "reviewed"
    ARCHIVED = "archived"

ContactStatusType = SQLEnum(
    ContactStatus,
    values_callable=lambda enum_cls: [member.value for member in enum_cls],
    validate_strings=True,
    name="contact_status_enum",
    native_enum=True,
)

class ContactMessage(Base):
    __tablename__ = "contact_message"


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)   
    email = Column(CITEXT, nullable=False)
    message = Column(Text, nullable=False)
    source = Column(String, nullable=False)
    status = Column(ContactStatusType, nullable=False, index=True, server_default=sa.text("'new'::contact_status_enum"))

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )
    updated_at = Column( DateTime(timezone=True), nullable=False,server_default=sa.func.now(),onupdate=sa.func.now())
    message_hash = Column(String(32), nullable=False)
    created_at_date = Column(Date, nullable=False, server_default=sa.func.current_date())
    @validates("message")
    def _sync_message_hash(self, key, value: str) -> str:
        self.message_hash = hashlib.md5(value.encode("utf-8")).hexdigest()
        return value

    processed_at = Column(DateTime(timezone=True), nullable=True)

    # related_object_type = 'contact_message'
    # related_object_id = ContactMessage.id

    __table_args__ = (
        # Антиспам: один и тот же email + то же сообщение — не чаще 1 раза в день
        UniqueConstraint(
         "email",
         "message_hash",
         "created_at_date",
         name="uq_contact_message_per_day",
     ),

        # Быстрые выборки
        Index("ix_contact_message_created_at_desc", sa.text("created_at DESC")),
        Index("ix_contact_message_status", "status"),

        # Базовая валидация содержимого
        CheckConstraint("char_length(name) > 0", name="ck_contact_name_nonempty"),
        CheckConstraint("char_length(message) > 0", name="ck_contact_message_nonempty"),
    )
@event.listens_for(ContactMessage, "before_insert")
def _set_created_at_fields(_, __, target: ContactMessage) -> None:
    if target.created_at is None:
        target.created_at = datetime.now(timezone.utc)
    if target.created_at_date is None:
        target.created_at_date = target.created_at.date()    
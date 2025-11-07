from __future__ import annotations

import enum
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import (
    Column, String, Text, DateTime,
    CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID, CITEXT
from sqlalchemy.types import Enum as SQLEnum
from app.models.application import ApplicationStatusType
from app.models.taxonomy import LanguageEnumType
from app.core.db import Base


# ======================================================
#                     ContactMessage
# ======================================================

class ContactStatus(enum.Enum):

    NEW = "new"
    REVIEWED = "reviewed"
    ARCHIVED = "archived"

ContactStatusType = SQLEnum(ContactStatus, name="contact_status_enum", native_enum=True)

class ContactMessage(Base):
    __tablename__ = "contact_message"


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)   
    email = Column(CITEXT, nullable=False)
    message = Column(Text, nullable=False)
    source = Column(String, nullable=False)
    status = Column(ContactStatusType, nullable=False, index=True, server_default=sa.text("'new'::contact_status_enum"))

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=sa.text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=sa.text("now()"), onupdate=sa.text("now()"))

    processed_at = Column(DateTime(timezone=True), nullable=True)

    # related_object_type = 'contact_message'
    # related_object_id = ContactMessage.id

    __table_args__ = (
        # Антиспам: один и тот же email + то же сообщение — не чаще 1 раза в день
        UniqueConstraint(
            "email",
            sa.text("md5(message)"),
            sa.text("created_at::date"),
            name="uq_contact_message_per_day"
        ),

        # Быстрые выборки
        Index("ix_contact_message_created_at_desc", sa.text("created_at DESC")),
        Index("ix_contact_message_status", "status"),

        # Базовая валидация содержимого
        CheckConstraint("char_length(name) > 0", name="ck_contact_name_nonempty"),
        CheckConstraint("char_length(message) > 0", name="ck_contact_message_nonempty"),
    )
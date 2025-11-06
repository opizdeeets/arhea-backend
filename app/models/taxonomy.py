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
#                     I18N ENUM
# ======================================================
class LanguageEnum(enum.Enum):
    EN = "en"
    RU = "ru"
    TK = "tk"

LanguageEnumType = SQLEnum(LanguageEnum, name="language_enum", native_enum=True)







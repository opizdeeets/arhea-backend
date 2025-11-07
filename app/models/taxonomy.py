from __future__ import annotations
import enum
from sqlalchemy.types import Enum as SQLEnum

# ======================================================
#                     I18N ENUM
# ======================================================
class LanguageEnum(enum.Enum):
    EN = "en"
    RU = "ru"
    TK = "tk"

LanguageEnumType = SQLEnum(LanguageEnum, name="language_enum", native_enum=True)







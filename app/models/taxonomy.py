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

LanguageEnumType = SQLEnum(
    LanguageEnum,
    values_callable=lambda enum_cls: [member.value for member in enum_cls],
    validate_strings=True,
    name="language_enum",
    native_enum=True,
)





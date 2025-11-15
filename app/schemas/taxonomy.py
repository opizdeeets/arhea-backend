from pydantic import BaseModel
from app.models.taxonomy import LanguageEnum


class LanguageRead(BaseModel):
    value: LanguageEnum
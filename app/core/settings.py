from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl, Field
from typing import Optional, Union

class Settings(BaseSettings):
   model_config = SettingsConfigDict(
      env_file = ".env",
      env_file_encoding = "utf-8",
      extra="ignore",
   )

   DATABASE_URL: AnyUrl = Field(..., description="PostgreSQL DSN (asyncpg)")
   
   DATABASE_SYNC_URL: Optional[Union[AnyUrl, str]] = Field(default=None, description="PostgreSQL DSN (psycopg2) for migrations")

   DEBUG: bool = Field(default=False)
   ALLOWED_ORIGINS: str = Field(default="*")
   

settings = Settings()   
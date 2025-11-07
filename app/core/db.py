from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import AsyncGenerator
# from app.models.project import *

DATABASE_URL = "postgresql+asyncpg://arhea_admin:arhea@127.0.0.1:5432/arhea_db"


engine = create_async_engine(DATABASE_URL, echo = True)

AsyncSessionLocal = sessionmaker(
    bind = engine,
    class_= AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
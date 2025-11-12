from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
from app.core.settings import settings  



engine = create_async_engine(
    str(settings.DATABASE_URL),
    pool_size = 5,
    max_overflow = 10,
    pool_pre_ping=True
)

async_session = async_sessionmaker(engine, expore_on_commit=False, class_=AsyncSession)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    session = async_session()
    try:
        yield session
    finally:
        await session.close()
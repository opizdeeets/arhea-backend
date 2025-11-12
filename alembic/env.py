from __future__ import annotations
import os, sys
from pathlib import Path
from logging.config import fileConfig
from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

# 0) sys.path + .env
ROOT = Path(__file__).resolve().parents[1]  # корень репозитория
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv  # pip install python-dotenv
    load_dotenv(ROOT / ".env")
except Exception:
    pass

# 1) alembic config
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 2) импортируем Base И ВСЕ МОДЕЛИ
from app.core.db import Base

import app.models.location
import app.models.career
import app.models.contact
import app.models.media
import app.models.news
import app.models.people
import app.models.taxonomy
import app.models.project 


# ВАЖНО: явно подтянуть модули с моделями, чтобы они зарегистрировались в Base.metadata
# подстрой пути под своё дерево
# если все модели в одном файле

target_metadata = Base.metadata

ASYNC_URL = os.getenv("DATABASE_URL")
SYNC_URL = os.getenv("DATABASE_SYNC_URL") or config.get_main_option("sqlalchemy.url")

def run_migrations_offline() -> None:
    url = SYNC_URL or ASYNC_URL
    if not url:
        raise RuntimeError("Set DATABASE_SYNC_URL or sqlalchemy.url in alembic.ini")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    url = ASYNC_URL or SYNC_URL
    if not url:
        raise RuntimeError("Set DATABASE_URL or DATABASE_SYNC_URL")
    engine = create_async_engine(url, poolclass=pool.NullPool)
    async with engine.connect() as conn:
        await conn.run_sync(do_run_migrations)
    await engine.dispose()

def run() -> None:
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        import asyncio
        asyncio.run(run_migrations_online())

run()

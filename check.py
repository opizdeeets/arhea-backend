import asyncio
from app.core.db import engine
import sqlalchemy as sa

async def ping():
    async with engine.connect() as conn:
        r = await conn.execute(sa.text("SELECT 1"))
        print(r.scalar())  # должен быть 1

asyncio.run(ping())
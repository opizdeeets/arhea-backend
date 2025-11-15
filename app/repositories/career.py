from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.career import Career
from app.repositories.base import BaseRepository


class CareerRepository(BaseRepository[Career]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Career)  

    async def list_published(self, locale: str | None = None, limit: int | None = None) -> list[Career]:
        filters = {"is_published": True}
        order_by = ["-order_index"]
        return await self.list(filters=filters, order_by=order_by, limit=limit)

    def _relations_options(self):
        return (
            selectinload(Career.translations),
        )

    async def get_with_relations(self, career_id: UUID) -> Career | None:
        stmt = (
            sa.select(Career)
            .where(Career.id == career_id)
            .options(*self._relations_options())
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def list_published_with_relations(self, limit: int | None = None) -> list[Career]:
        stmt = (
            sa.select(Career)
            .where(Career.is_published.is_(True))
            .order_by(Career.order_index.desc())
            .options(*self._relations_options())
        )
        if limit is not None:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.location import Location
from app.repositories.base import BaseRepository


class LocationRepository(BaseRepository[Location]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Location)  

    def _relations_options(self):
        return (
            selectinload(Location.translations),
        )

    async def get_with_relations(self, location_id: UUID) -> Location | None:
        stmt = (
            sa.select(Location)
            .where(Location.id == location_id)
            .options(*self._relations_options())
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def list_with_relations(self, limit: int | None = None) -> list[Location]:
        stmt = (
            sa.select(Location)
            .order_by(Location.order_index.asc())
            .options(*self._relations_options())
        )
        if limit is not None:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.project import ProjectStyle, ProjectType
from app.repositories.base import BaseRepository


class ProjectTypeRepository(BaseRepository[ProjectType]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ProjectType)

    def _relations_options(self):
        return (
            selectinload(ProjectType.translations),
        )

    async def get_with_relations(self, type_id: UUID) -> ProjectType | None:
        stmt = (
            sa.select(ProjectType)
            .where(ProjectType.id == type_id)
            .options(*self._relations_options())
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def list_visible_with_relations(self, limit: int | None = None) -> list[ProjectType]:
        stmt = (
            sa.select(ProjectType)
            .where(ProjectType.visible.is_(True))
            .order_by(ProjectType.order_index.asc())
            .options(*self._relations_options())
        )
        if limit is not None:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return result.unique().scalars().all()


class ProjectStyleRepository(BaseRepository[ProjectStyle]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ProjectStyle)

    def _relations_options(self):
        return (
            selectinload(ProjectStyle.translations),
        )

    async def get_with_relations(self, style_id: UUID) -> ProjectStyle | None:
        stmt = (
            sa.select(ProjectStyle)
            .where(ProjectStyle.id == style_id)
            .options(*self._relations_options())
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def list_visible_with_relations(self, limit: int | None = None) -> list[ProjectStyle]:
        stmt = (
            sa.select(ProjectStyle)
            .where(ProjectStyle.visible.is_(True))
            .order_by(ProjectStyle.order_index.asc())
            .options(*self._relations_options())
        )
        if limit is not None:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

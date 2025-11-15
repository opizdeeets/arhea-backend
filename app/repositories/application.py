from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.application import Application
from app.models.career import Career
from app.models.media import MediaAsset
from app.repositories.base import BaseRepository


class ApplicationRepository(BaseRepository[Application]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Application)  

    def _relations_options(self):
        files_option = selectinload(Application.files).selectinload(MediaAsset.translations)
        career_option = selectinload(Application.career).selectinload(Career.translations)

        return (
            files_option,
            career_option,
        )

    async def get_with_relations(self, application_id: UUID) -> Application | None:
        stmt = (
            sa.select(Application)
            .where(Application.id == application_id)
            .options(*self._relations_options())
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def list_with_relations(self, limit: int | None = None) -> list[Application]:
        stmt = (
            sa.select(Application)
            .order_by(Application.created_at.desc())
            .options(*self._relations_options())
        )
        if limit is not None:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

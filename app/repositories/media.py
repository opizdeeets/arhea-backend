from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.application import Application
from app.models.career import Career
from app.models.media import MediaAsset
from app.repositories.base import BaseRepository


class MediaAssetRepository(BaseRepository[MediaAsset]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, MediaAsset)  

    def _relations_options(self):
        application_option = selectinload(MediaAsset.application)
        application_option.selectinload(Application.career).selectinload(Career.translations)

        return (
            selectinload(MediaAsset.translations),
            application_option,
        )

    async def get_with_relations(self, media_id: UUID) -> MediaAsset | None:
        stmt = (
            sa.select(MediaAsset)
            .where(MediaAsset.id == media_id)
            .options(*self._relations_options())
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def list_with_relations(self, limit: int | None = None) -> list[MediaAsset]:
        stmt = (
            sa.select(MediaAsset)
            .order_by(MediaAsset.created_at.desc())
            .options(*self._relations_options())
        )
        if limit is not None:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

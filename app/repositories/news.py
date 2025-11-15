from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.media import MediaAsset
from app.models.news import News, NewsMedia
from app.repositories.base import BaseRepository


class NewsRepository(BaseRepository[News]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, News)  

    async def list_published(self, limit: int | None = None) -> list[News]:
        filters = {"is_published": True}
        order_by = ["-published_at"]
        return await self.list(filters=filters, order_by=order_by, limit=limit)

    def _relations_options(self):
        media_option = (
            selectinload(News.media_items)
            .selectinload(NewsMedia.media)
            .selectinload(MediaAsset.translations)
        )

        return (
            selectinload(News.translations),
            media_option,
        )

    async def get_with_relations(self, news_id: UUID) -> News | None:
        stmt = (
            sa.select(News)
            .where(News.id == news_id)
            .options(*self._relations_options())
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def list_published_with_relations(self, limit: int | None = None) -> list[News]:
        stmt = (
            sa.select(News)
            .where(News.is_published.is_(True))
            .order_by(News.published_at.desc())
            .options(*self._relations_options())
        )
        if limit is not None:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return result.unique().scalars().all()
    

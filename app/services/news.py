from sqlalchemy.ext.asyncio import AsyncSession
from app.models.news import News
from app.core.errors import DomainError
from uuid import UUID
from app.repositories.news import NewsRepository
from app.schemas.news import NewsCreate, NewsUpdate



# ---------------- GET ----------------
async def get_news(session: AsyncSession, news_id: UUID) -> News:
    repo = NewsRepository(session)
    news = await repo.get(news_id)
    if news is None:
        raise DomainError("not_found", "news not found", status=404, details={"id": news_id})
    return news


# ---------------- GET LIST ----------------    
async def get_news_list(session: AsyncSession, limit: int | None = None) -> list[News]:
    repo = NewsRepository(session)
    return await repo.list_published(limit=limit)



# ---------------- CREATE ----------------    
async def create_news(session: AsyncSession, data: NewsCreate) -> News:
    repo = NewsRepository(session)
    payload = data.model_dump()
    if not payload.get("preview"):
        payload["preview"] = payload.get("short_description") or ""
    news = await repo.create(payload)
    await session.commit()
    await session.refresh(news)
    return news


# ---------------- UPDATE ----------------    
async def update_news(session: AsyncSession, news_id: UUID, data: NewsUpdate) -> News:
    repo = NewsRepository(session)
    payload = data.model_dump(exclude_unset=True)
    if not payload:
        raise DomainError("empty_update", "nothing to update", status=400)
    if "short_description" in payload and "preview" not in payload:
        payload["preview"] = payload["short_description"] or ""
    news = await repo.update(news_id, payload)
    if news is None:
        raise DomainError("not_found", "news not found", status=404, details={"id": news_id})
    await session.commit()
    await session.refresh(news)
    return news    


# ---------------- DELETE ----------------    
async def delete_news(session: AsyncSession, news_id: UUID) -> bool:
    repo = NewsRepository(session)
    deleted = await repo.delete(news_id)
    if not deleted:
        raise DomainError("not_found", "news not found", status=404, details={"id": news_id})
    await session.commit()
    return True
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.contact import ContactMessage 
from app.repositories.base import BaseRepository
from app.core.errors import DomainError
from typing import Any


class ContactMessageRepository(BaseRepository[ContactMessage]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ContactMessage)  

    async def create_message(self, data: dict[str, Any]) -> ContactMessage:
        if not isinstance(data, dict) or not data:
            raise DomainError("invalid_data", "message payload is empty", status=400)
        return await self.create(data)
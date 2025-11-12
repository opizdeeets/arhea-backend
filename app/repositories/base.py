from typing import Any, Mapping, Optional, Sequence, Type, TypeVar
from sqlalchemy import select
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Load


T = TypeVar("T")


class BaseRepository[T]:
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def get(self, id: Any, options: Optional[Sequence[Load]] = None) -> Optional[T]:
        if options is None:
            stmt = select(self.model).where(self.model.id == id)
        else:            
            stmt = select(self.model).where(self.model.id == id).options(*options)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list(self, 
        filters: Optional[Mapping[str, Any]] = None, 
        order_by: Optional[Sequence[Any]] = None, 
        limit: Optional[int] = None, 
        options: Optional[Sequence[Load]] = None) -> list[T]:

        stmt = select(self.model)
        if filters is not None:
            for k,v in filters.items():
                stmt = stmt.where(getattr(self.model, k) == v)
        if order_by is not None:
            stmt = stmt.order_by(*order_by)
        if limit is not None:
            stmt = stmt.limit(limit)
        if options is not None:
            stmt = stmt.options(*options)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def exists(self, filters: Optional[Mapping[str, Any]] = None) -> bool:
        stmt = select(sa.literal(True)).select_from(self.model).limit(1)
        if filters is not None:  
            for k, v in filters.items():
                stmt = stmt.where(getattr(self.model, k) == v)
        result = await self.session.execute(stmt)
        return bool(result.scalar_one_or_none())                

    async def create(self, data: Mapping[str, Any]) -> T:
        obj = self.model(**data)
        self.session.add(obj)
        return obj
    
    async def update(self, id: Any, data: Mapping[str, Any]) -> Optional[T]:
        obj = await self.get(id)
        if obj is None:
            return None
        for k,v in data.items():
            setattr(obj, k,v)
        return obj

    async def delete(self, id: Any) -> bool:
        obj = await self.get(id) 
        if obj is None:
            return False
        await self.session.delete(obj)
        return True
    

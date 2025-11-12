from sqlalchemy import select
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload, Load
from app.models.career import Career, CareerI18n
from app.repositories.base import BaseRepository

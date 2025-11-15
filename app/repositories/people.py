from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.media import MediaAsset
from app.models.people import Person, PersonRole, ProjectPersonRole
from app.models.project import Project
from app.repositories.base import BaseRepository


class PersonRepository(BaseRepository[Person]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Person)  

    def _relations_options(self):
        photo_option = (
            selectinload(Person.photo)
            .selectinload(MediaAsset.translations)
        )

        roles_option = selectinload(Person.project_roles)
        role_loader = roles_option.selectinload(ProjectPersonRole.role)
        role_loader.selectinload(PersonRole.translations)
        project_loader = roles_option.selectinload(ProjectPersonRole.project)
        project_loader.selectinload(Project.translations)

        return (
            selectinload(Person.translations),
            photo_option,
            roles_option,
        )

    async def get_with_relations(self, person_id: UUID) -> Person | None:
        stmt = (
            sa.select(Person)
            .where(Person.id == person_id)
            .options(*self._relations_options())
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def list_published_with_relations(self, limit: int | None = None) -> list[Person]:
        stmt = (
            sa.select(Person)
            .where(Person.is_published.is_(True))
            .order_by(Person.order_index.desc())
            .options(*self._relations_options())
        )
        if limit is not None:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

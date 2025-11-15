from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.location import Location
from app.models.media import MediaAsset
from app.models.people import Person, PersonRole, ProjectPersonRole
from app.models.project import Project, ProjectMedia, ProjectStyle, ProjectType
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Project)

    async def list_published_for_main(self, limit: int | None = None) -> list[Project]:
        filters = {"is_published": True}
        order_by = ["-order_index"]
        return await self.list(filters=filters, order_by=order_by, limit=limit)

    def _relations_options(self):
        media_option = selectinload(Project.media)
        media_asset_option = media_option.selectinload(ProjectMedia.media)
        media_asset_option.selectinload(MediaAsset.translations)

        cover_option = selectinload(Project.cover)
        cover_option.selectinload(MediaAsset.translations)

        location_option = selectinload(Project.location)
        location_option.selectinload(Location.translations)

        project_type_option = selectinload(Project.project_type)
        project_type_option.selectinload(ProjectType.translations)

        styles_option = selectinload(Project.styles)
        styles_option.selectinload(ProjectStyle.translations)

        person_roles_option = selectinload(Project.person_roles)
        person_loader = person_roles_option.selectinload(ProjectPersonRole.person)
        person_loader.selectinload(Person.translations)
        role_loader = person_roles_option.selectinload(ProjectPersonRole.role)
        role_loader.selectinload(PersonRole.translations)

        return (
            selectinload(Project.translations),
            media_option,
            cover_option,
            location_option,
            project_type_option,
            styles_option,
            person_roles_option,
        )

    async def get_with_relations(self, project_id: UUID) -> Project | None:
        stmt = (
            sa.select(Project)
            .where(Project.id == project_id)
            .options(*self._relations_options())
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def list_published_with_relations(self, limit: int | None = None) -> list[Project]:
        stmt = (
            sa.select(Project)
            .where(Project.is_published.is_(True))
            .order_by(Project.order_index.desc(), Project.published_at.desc())
            .options(*self._relations_options())
        )
        if limit is not None:
            if limit <= 0 or limit > 100:
                raise ValueError("limit must be 1..100")
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

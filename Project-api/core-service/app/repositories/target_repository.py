from typing import Type
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.target import Target
from ..db.models.projects import Project
from .sqlalchemy_repository import SqlAlchemyRepository


class TargetRepository(SqlAlchemyRepository[Target]):
    """
    Наследуется от SqlAlchemyRepository - получает
    create/get_single/get_multi/update/delete для Target как есть.
    Добавляет ровно один метод, которого в generic-слое быть не может:
    фильтр по organization_id требует JOIN через Project,
    а не просто filter_by по полю самой модели Target.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(Target, session)

    async def get_by_organization(
        self, organization_id: UUID, *, limit: int = 100, offset: int = 0
    ) -> list[Target]:
        stmt = (
            select(Target)
            .join(Project, Target.project_id == Project.id)
            .where(Project.organization_id == organization_id)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

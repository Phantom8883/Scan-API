from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.organization import OrganizationMembership


class MembershipRepository:
    """
    Не наследуется от AbstractRepository - у OrganizationMembership
    составной первичный ключ (user_id + organization_id), а не единый id,
    на который рассчитан наш общий контракт. Поэтому здесь свой,
    маленький репозиторий ровно с тем одним методом, который нужен.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session


    async def get(self, user_id: UUID, organization_id: UUID) -> OrganizationMembership | None:
        stmt = select(OrganizationMembership).filter_by(
            user_id=user_id,
            organization_id=organization_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
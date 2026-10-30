from uuid import UUID

from ..repositories.base_repository import AbstractRepository
from ..services.base_service import BaseService
from ..db.models.target import Target
from ..repositories.target_repository import TargetRepository


class TargetService(BaseService[Target]):
    def __init__(self, repository: TargetRepository):
        super().__init__(repository)
        self.repository: TargetRepository = repository

    async def list_for_organization(
        self, organization_id: UUID, *, limit: int = 100, offset: int = 0
    ) -> list[Target]:
        return await self.repository.get_by_organization(
            organization_id, limit=limit, offset=offset
        )

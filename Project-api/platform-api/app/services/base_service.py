from typing import Any, Generic
from uuid import UUID

from app.repositories.base_repository import AbstractRepository, ModelType

class BaseService(Generic[ModelType]):
    """
    Тонкая обертка над репозиторием.
    Сюда позже будет добавляться реальная бизнес-логика
    (проверки, события, вызовы других сервисов) -
    а не прямой SQL, для этого есть репозиторий.
    """

    def __init__(self, repository: AbstractRepository[ModelType]):
        self.repository = repository

    async def create(self, **fields: Any) -> ModelType:
        return await self.repository.create(**fields)

    async def get(self, pk: UUID) -> ModelType | None:
        return await self.repository.get_single(id=pk)

    async def list(self, *, limit: int = 100, offset: int = 0, **filters: Any) -> list[ModelType]:
        return await self.repository.get_multi(limit=limit, offset=offset, **filters)

    async def update(self, pk: UUID, **fields: Any) -> ModelType | None:
        return await self.repository.update(pk, **fields)

    async def delete(self, pk: UUID) -> None:
        await self.repository.delete(pk)
        
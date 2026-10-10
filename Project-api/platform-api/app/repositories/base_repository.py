from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar
from uuid import UUID

ModelType = TypeVar("ModelType")

class AbstractRepository(ABC, Generic[ModelType]):
    """
    Контракт: что обязан уметь любой репозитой,
    назависимо от того, что у него внутриу - PostgreSQL, Redis, Mongo.
    Сервис будет зависеть от ЭТОГО интерфейса, а не от конкретной SQLAlchemy-реализации.
    """

    @abstractmethod
    async def create(self, **fields: Any) -> ModelType:
        raise NotImplementedError

    @abstractmethod
    async def get_single(self, **fields: Any) -> ModelType | None:
        raise NotImplementedError

    @abstractmethod
    async def get_multi(self, *, limit: int = 100, offset: int = 0, **filters: Any) -> list[ModelType]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, pk: UUID, **fields: Any) -> ModelType | None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, pk: UUID) -> None:
        raise NotImplementedError
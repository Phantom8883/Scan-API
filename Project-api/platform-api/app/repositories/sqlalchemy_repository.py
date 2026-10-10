from typing import Any, Generic, Type
from uuid import UUID

from sqlalchemy import select, update as sa_update, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User

from .base_repository import AbstractRepository, ModelType


class SqlAlchemyRepository(AbstractRepository[ModelType], Generic[ModelType]):
    """
    Сюда передаётся УЖЕ ГОТОВАЯ сессия на один HTTP-запрos
    (та, что отдаёт get_db dependency) - а не фабрика сессий,
    как было в разобранном нами шаблоне (там это и было багом:
    аннотация типа врала, что это AsyncSession, а вызывалась она
    как функция-фабрика).

    Репозиторий НЕ управляет жизненным циклом сессии и НЕ делает commit —
    этим будет заниматься сервис (или вызывающий код). Если бы репозиторий
    сам коммитил, то сервис, которому нужно изменить два репозитория
    в одной транзакции, не смог бы откатить оба разом при ошибке.
    """


    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, **fields: Any) -> ModelType:
        instance = self.model(**fields)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def get_single(self, **filters: Any) -> ModelType | None:
        stmt = select(self.model).filter_by(**filters)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(
        self, *, order_by: str = "created_at", limit: int = 100, offset: int = 0, **filters: Any
    ) -> list[ModelType]:
        column = getattr(self.model, order_by)
        stmt = (
            select(self.model)
            .filter_by(**filters)
            .order_by(column)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, pk: UUID, **fields: Any) -> ModelType | None:
        if not fields:
            return await self.get_single(id=pk)
        stmt = (
            sa_update(self.model)
            .where(self.model.id == pk)
            .values(**fields)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, pk: UUID) -> None:
        await self.session.execute(sa_delete(self.model).where(self.model.id == pk))

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .db.session import get_session
from .db.models.job import Job
from .db.models.user import User
from .repositories.sqlalchemy_repository import SqlAlchemyRepository
from .services.base_service import BaseService


async def get_job_repository(
        session: AsyncSession = Depends(get_session),
) -> SqlAlchemyRepository[Job]:
    return SqlAlchemyRepository(Job, session)


async def get_job_service(
        repo: SqlAlchemyRepository[Job] = Depends(get_job_repository),
) -> BaseService[Job]:
    return BaseService(repo)


async def get_user_repository(
        session: AsyncSession = Depends(get_session)
) -> SqlAlchemyRepository[User]:
    return SqlAlchemyRepository(User, session)


async def get_user_service(
        repo: SqlAlchemyRepository[User] = Depends(get_user_repository)
) -> BaseService[User]:
    return BaseService(repo)
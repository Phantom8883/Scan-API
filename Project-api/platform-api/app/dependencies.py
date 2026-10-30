from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession

from .db.session import get_session
from .db.models.job import Job
from .db.models.user import User
from .db.models.target import Target

from .repositories.sqlalchemy_repository import SqlAlchemyRepository
from .repositories.membership_repository import MembershipRepository
from .repositories.target_repository import TargetRepository

from .services.target_service import TargetService
from .services.base_service import BaseService

from .core.security import decode_token

from uuid import UUID

import jwt

oath2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_job_repository(
    session: AsyncSession = Depends(get_session),
) -> SqlAlchemyRepository[Job]:
    return SqlAlchemyRepository(Job, session)


async def get_job_service(
    repo: SqlAlchemyRepository[Job] = Depends(get_job_repository),
) -> BaseService[Job]:
    return BaseService(repo)


async def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> SqlAlchemyRepository[User]:
    return SqlAlchemyRepository(User, session)


async def get_user_service(
    repo: SqlAlchemyRepository[User] = Depends(get_user_repository),
) -> BaseService[User]:
    return BaseService(repo)


async def get_target_repository(
    session: AsyncSession = Depends(get_session),
) -> TargetRepository:
    return TargetRepository(session)


async def get_target_service(
    repo: TargetRepository = Depends(get_target_repository),
) -> TargetService:
    return TargetService(repo)


async def get_current_user(
    token: str = Depends(oath2_scheme),
    service: BaseService[User] = Depends(get_user_service),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невалидный токен",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
    except jwt.InvalidTokenError:
        raise credentials_error

    if payload.get("type") != "access":
        raise credentials_error

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_error

    user = await service.get(UUID(user_id))
    if user is None:
        raise credentials_error

    return user


async def get_membership_repository(
    session: AsyncSession = Depends(get_session),
) -> MembershipRepository:
    return MembershipRepository(session)


def require_org_role(*allowed_roles: str):
    async def checker(
        organization_id: UUID,
        current_user: User = Depends(get_current_user),
        repo: MembershipRepository = Depends(get_membership_repository),
    ) -> User:
        membership = await repo.get(current_user.id, organization_id)

        if membership is None or membership.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="недостаточно прав"
            )

        return current_user

    return checker

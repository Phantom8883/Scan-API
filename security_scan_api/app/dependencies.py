from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session


async def get_db(
        session: AsyncSession = Depends(get_session),
) -> AsyncSession:
    """
    Наша зависимость верхнего уровня.

    Позже здесь можно будет объединять:
    auth + permission + rate limit и т.д.
    """

    return session
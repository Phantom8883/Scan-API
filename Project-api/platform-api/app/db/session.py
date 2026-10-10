import os 

from sqlalchemy.ext.asyncio import (
    AsyncSession, 
    async_sessionmaker,
    create_async_engine,
)


DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)


SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_session():
    """
    Создаёт одну AsyncSession на один запрос
    и закрывает её после завершения запроса.
    """

    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Scan
from app.schemas.scan import ScanUpdate


async def create_scan(
    session: AsyncSession,
    target: str,
    user_id: UUID,
) -> Scan:
    """
    Создаёт новую запись сканирования.
    """

    scan = Scan(
        target=target,
        user_id=user_id,
        status="pending",
    )

    session.add(scan)

    await session.commit()
    await session.refresh(scan)

    return scan


async def get_scan(
    session: AsyncSession,
    scan_id: UUID,
) -> Scan | None:
    """
    Получает сканирование по ID.
    """

    stmt = select(Scan).where(
        Scan.id == scan_id,
    )

    result = await session.execute(stmt)

    return result.scalar_one_or_none()


async def update_scan(
    session: AsyncSession,
    scan_id: UUID,
    update_data: ScanUpdate,
) -> Scan | None:
    """
    Обновляет только те поля,
    которые были переданы клиентом.

    Если сканирование не найдено,
    возвращает None.
    """

    scan = await get_scan(
        session,
        scan_id,
    )

    if scan is None:
        return None

    update_dict = update_data.model_dump(
        exclude_unset=True,
    )

    for key, value in update_dict.items():
        setattr(scan, key, value)

    await session.commit()
    await session.refresh(scan)

    return scan


async def delete_scan(
    session: AsyncSession,
    scan_id: UUID,
) -> bool:
    """
    Удаляет запись сканирования.

    Возвращает:
        True  — запись удалена.
        False — запись не найдена.
    """

    scan = await get_scan(
        session,
        scan_id,
    )

    if scan is None:
        return False

    await session.delete(scan)

    await session.commit()

    return True
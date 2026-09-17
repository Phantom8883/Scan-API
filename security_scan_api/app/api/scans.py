from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas.scan import (
    DeleteScanResponse,
    ScanCreate,
    ScanRead,
    ScanUpdate,
)
from app.services.scan import (
    create_scan,
    delete_scan,
    get_scan,
    update_scan,
)


router = APIRouter(
    prefix="/scans",
    tags=["scans"],
)


@router.post(
    "",
    response_model=ScanRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_scan_endpoint(
    data: ScanCreate,
    session: AsyncSession = Depends(get_db),
) -> ScanRead:
    """
    Создаёт новое сканирование.
    """

    # Временно, пока нет authentication.
    user_id = UUID("00000000-0000-0000-0000-000000000001")



    return await create_scan(
        session=session,
        target=data.target,
        user_id=user_id,
    )


@router.get(
    "/{scan_id}",
    response_model=ScanRead,
)
async def get_scan_endpoint(
    scan_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> ScanRead:
    """
    Получает сканирование по ID.
    """

    scan = await get_scan(
        session,
        scan_id,
    )

    if scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found",
        )

    return scan


@router.patch(
    "/{scan_id}",
    response_model=ScanRead,
)
async def patch_scan_endpoint(
    scan_id: UUID,
    scan_data: ScanUpdate,
    session: AsyncSession = Depends(get_db),
) -> ScanRead:
    """
    Частично обновляет сканирование.
    """

    updated_scan = await update_scan(
        session=session,
        scan_id=scan_id,
        update_data=scan_data,
    )

    if updated_scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found",
        )

    return updated_scan


@router.delete(
    "/{scan_id}",
    response_model=DeleteScanResponse,
)
async def delete_scan_endpoint(
    scan_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> DeleteScanResponse:
    """
    Удаляет сканирование.
    """

    success = await delete_scan(
        session,
        scan_id,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found",
        )

    return DeleteScanResponse(
        message="Scan deleted successfully",
        scan_id=scan_id,
    )
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ScanCreate(BaseModel):
    """
    Данные, которые клиент отправляет
    при создании сканирования.
    """

    target: str


class ScanRead(BaseModel):
    """
    Данные, которые API возвращает клиенту.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    target: str
    status: str
    result: str | None


class ScanUpdate(BaseModel):
    """
    Данные, которые клиент отправляет
    при частичном обновлении сканирования.
    """

    target: str | None = None
    status: str | None = None


class DeleteScanResponse(BaseModel):
    """
    Ответ API после удаления сканирования.
    """

    message: str
    scan_id: UUID
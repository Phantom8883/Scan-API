from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ExecutionCreate(BaseModel):
    """
    Команда на создание технического execution.

    Эти данные в будущем будут приходить
    от platform-api.
    """

    assessment_id: UUID
    user_id: UUID

    # Список targets, которые нужно проверить.
    targets: list[UUID]

    # Выбранные технические модули.
    #
    # Например:
    # nmap
    # dns
    # tls
    # http
    modules: list[str]

    # Ограничения конкретного запуска.
    policy: dict[str, Any] | None = None

    # Защищает от повторного создания
    # одинакового execution.
    idempotency_key: str | None = None


class ExecutionRead(BaseModel):
    """
    Данные execution, которые API возвращает клиенту.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    assessment_id: UUID
    user_id: UUID
    status: str
    idempotency_key: str | None
    correlation_id: UUID
    policy: dict[str, Any] | None

    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
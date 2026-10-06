from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class JobRead(BaseModel):
    """
    Информация о технической Job.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    execution_id: UUID

    target_snapshot_id: UUID | None

    module: str
    queue: str | None

    status: str

    attempts: int
    max_attempts: int

    celery_task_id: str | None

    error_code: str | None
    error_message: str | None

    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
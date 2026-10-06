from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ObservationRead(BaseModel):
    """
    Фактическое наблюдение scanner'а.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    job_id: UUID
    target_snapshot_id: UUID

    type: str
    data: dict[str, Any]

    fingerprint: str | None

    observed_at: datetime | None
    created_at: datetime
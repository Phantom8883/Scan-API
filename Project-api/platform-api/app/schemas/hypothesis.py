from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SecurityHypothesisRead(BaseModel):
    """
    Гипотеза, построенная Analysis Engine.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    execution_id: UUID
    target_snapshot_id: UUID | None

    category: str
    title: str
    description: str | None

    confidence: float | None
    status: str

    created_at: datetime


class SecurityHypothesisDetail(SecurityHypothesisRead):
    """
    Гипотеза вместе с наблюдениями,
    на которых она основана.
    """

    observation_ids: list[UUID]
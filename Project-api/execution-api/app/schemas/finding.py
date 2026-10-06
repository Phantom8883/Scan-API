from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class FindingCandidateRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    execution_id: UUID
    target_snapshot_id: UUID | None

    hypothesis_id: UUID | None
    validation_run_id: UUID | None

    title: str
    description: str | None

    severity: str | None
    confidence: float | None

    fingerprint: str | None
    status: str

    created_at: datetime

class FindingCandidateDetail(FindingCandidateRead):
    """
    Candidate вместе с ID наблюдений,
    на которых основан результат.
    """

    observation_ids: list[UUID]
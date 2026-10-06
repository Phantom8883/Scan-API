from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class FindingCreate(BaseModel):
    assessment_id: UUID
    target_id: UUID

    title: str
    description: str | None = None

    severity: str | None = None

    remediation: str | None = None


class FindingRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    assessment_id: UUID
    target_id: UUID

    title: str
    description: str | None

    severity: str | None
    status: str

    remediation: str | None

    created_at: datetime
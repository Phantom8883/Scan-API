from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TargetCreate(BaseModel):
    project_id: UUID
    value: str
    target_type: str


class TargetRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    project_id: UUID

    value: str
    target_type: str
    normalized_value: str | None

    status: str
    created_at: datetime


class TargetVerificationRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    target_id: UUID

    verification_type: str
    verified: bool
    verified_at: datetime
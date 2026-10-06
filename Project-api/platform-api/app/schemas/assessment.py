from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AssessmentCreate(BaseModel):
    project_id: UUID

    # Target IDs, которые будут входить
    # в assessment.
    target_ids: list[UUID]

    # Настройки assessment.
    configuration: dict[str, Any] | None = None


class AssessmentRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    project_id: UUID
    created_by_user_id: UUID

    status: str
    configuration: dict[str, Any] | None

    created_at: datetime


class AssessmentTargetRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    assessment_id: UUID
    target_id: UUID
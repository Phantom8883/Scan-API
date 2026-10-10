from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ValidationPlanRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    hypothesis_id: UUID

    objective: str

    input_data: dict[str, Any] | None

    expected_secure_behavior: str | None
    expected_insecure_behavior: str | None

    success_criteria: dict[str, Any] | None
    constraints: dict[str, Any] | None

    status: str

    created_at: datetime


class ValidationRunRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    plan_id: UUID
    execution_id: UUID
    job_id: UUID | None

    status: str

    started_at: datetime | None
    finished_at: datetime | None


class ValidationResultRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    run_id: UUID

    success: bool
    confidence: float | None

    baseline: dict[str, Any] | None
    observed_state: dict[str, Any] | None
    observed_changes: dict[str, Any] | None

    data_exposure: dict[str, Any] | None

    state_changed: bool | None

    summary: str | None

    created_at: datetime
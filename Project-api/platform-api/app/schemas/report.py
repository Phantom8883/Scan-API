from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ReportCreate(BaseModel):
    assessment_id: UUID
    report_type: str
    storage_key: str


class ReportRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    assessment_id: UUID

    report_type: str
    storage_key: str

    created_at: datetime
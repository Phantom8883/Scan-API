from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EvidenceRead(BaseModel):
    """
    Метаданные evidence.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    observation_id: UUID

    storage_provider: str
    storage_key: str

    sha256: str
    content_type: str
    size_bytes: int

    created_at: datetime
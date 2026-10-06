from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Evidence(Base):
    __tablename__ = "evidence"

    # ID evidence.
    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Observation, которую подтверждает evidence.
    observation_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("observations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Storage provider.
    #
    # minio / s3
    storage_provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Ключ объекта в storage.
    storage_key: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    # SHA-256 содержимого.
    sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    # MIME type.
    content_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Размер файла в байтах.
    size_bytes: Mapped[int] = mapped_column(
        nullable=False,
    )

    # Когда evidence создан.
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    observation: Mapped["Observation"] = relationship(
        back_populates="evidence",
    )
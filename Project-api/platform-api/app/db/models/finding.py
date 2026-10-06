from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Finding(Base):
    __tablename__ = "findings"

    # ID finding.
    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Assessment, в котором проблема обнаружена.
    assessment_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Target, к которому относится finding.
    target_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("targets.id"),
        nullable=False,
        index=True,
    )

    # Название проблемы.
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Описание проблемы.
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # info / low / medium / high / critical
    severity: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    # open / resolved / accepted / false_positive
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="open",
        index=True,
    )

    # Что нужно исправить.
    remediation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Когда finding создан.
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    assessment: Mapped["Assessment"] = relationship(
        back_populates="findings",
    )
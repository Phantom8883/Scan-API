from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Report(Base):
    __tablename__ = "reports"

    # ID отчёта.
    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Assessment, по которому создан отчёт.
    assessment_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Например:
    # technical / executive / developer
    report_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Где хранится физический файл.
    storage_key: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    # Когда отчёт создан.
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    assessment: Mapped["Assessment"] = relationship(
        back_populates="reports",
    )
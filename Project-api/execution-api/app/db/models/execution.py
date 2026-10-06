from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Execution(Base):
    __tablename__ = "executions"

    # ID конкретного технического запуска.
    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # ID Assessment из platform-api.
    # Это внешний UUID, не ForeignKey.
    assessment_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        index=True,
    )

    # ID пользователя из platform-api.
    # Тоже внешний UUID.
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        index=True,
    )

    # pending / queued / running /
    # completed / failed / cancelled
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        index=True,
    )

    # Защита от повторного выполнения
    # одинакового запроса.
    idempotency_key: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    # Используется для связывания логов одной операции.
    correlation_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        default=uuid4,
        index=True,
    )

    # Зафиксированная политика выполнения.
    policy: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    started_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    target_snapshots: Mapped[list["TargetSnapshot"]] = relationship(
        back_populates="execution",
        cascade="all, delete-orphan",
    )

    jobs: Mapped[list["Job"]] = relationship(
        back_populates="execution",
        cascade="all, delete-orphan",
    )

    finding_candidates: Mapped[list["FindingCandidate"]] = relationship(
        back_populates="execution",
        cascade="all, delete-orphan",
    )

    hypotheses: Mapped[list["SecurityHypothesis"]] = relationship(
        back_populates="execution",
        cascade="all, delete-orphan",
    )
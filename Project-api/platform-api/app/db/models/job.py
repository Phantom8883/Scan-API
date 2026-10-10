from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Job(Base):
    __tablename__ = "jobs"

    # ID нашей задачи.
    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Execution, частью которого является Job.
    execution_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Target конкретной задачи.
    #
    # Может быть NULL для job,
    # работающей со всем execution.
    target_snapshot_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("target_snapshots.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Технический модуль.
    #
    # nmap / dns / tls / http / analysis
    module: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    # Очередь Celery.
    #
    # recon / web / analysis
    queue: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # queued / running / completed /
    # failed / retrying / cancelled
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="queued",
        index=True,
    )

    # Текущая попытка.
    attempts: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
    )

    # Максимальное количество попыток.
    max_attempts: Mapped[int] = mapped_column(
        nullable=False,
        default=3,
    )

    # ID соответствующей Celery task.
    celery_task_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    # Машиночитаемый код ошибки.
    error_code: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Подробность ошибки.
    error_message: Mapped[str | None] = mapped_column(
        String(2000),
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

    execution: Mapped["Execution"] = relationship(
        back_populates="jobs",
    )

    target_snapshot: Mapped["TargetSnapshot | None"] = relationship(
        back_populates="jobs",
    )

    observations: Mapped[list["Observation"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )
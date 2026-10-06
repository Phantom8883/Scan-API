from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TargetSnapshot(Base):
    __tablename__ = "target_snapshots"

    # ID snapshot.
    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Execution, к которому относится snapshot.
    execution_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ID исходного Target из platform-api.
    source_target_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Значение target на момент запуска.
    target: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # domain / ip / url / network
    target_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Нормализованное значение.
    normalized_target: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # IP-адреса, полученные во время создания snapshot.
    resolved_addresses: Mapped[list[str] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # Дополнительные данные scope.
    scope_metadata: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    execution: Mapped["Execution"] = relationship(
        back_populates="target_snapshots",
    )

    jobs: Mapped[list["Job"]] = relationship(
        back_populates="target_snapshot",
        passive_deletes=True,
    )

    observations: Mapped[list["Observation"]] = relationship(
        back_populates="target_snapshot",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
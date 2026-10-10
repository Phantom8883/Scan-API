from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Observation(Base):
    __tablename__ = "observations"

    # ID наблюдения.
    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Job, которая обнаружила факт.
    job_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Target, к которому относится факт.
    target_snapshot_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("target_snapshots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Тип факта.
    #
    # open_port
    # dns_record
    # http_header
    # tls_certificate
    type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    # Сами данные факта.
    data: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
    )

    # Отпечаток для дедупликации.
    fingerprint: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    # Когда scanner обнаружил факт.
    observed_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    # Когда observation записали в БД.
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    job: Mapped["Job"] = relationship(
        back_populates="observations",
    )

    target_snapshot: Mapped["TargetSnapshot"] = relationship(
        back_populates="observations",
    )

    evidence: Mapped[list["Evidence"]] = relationship(
        back_populates="observation",
        cascade="all, delete-orphan",
    )

    finding_candidates: Mapped[list["FindingCandidate"]] = relationship(
        secondary="finding_observations",
        back_populates="observations",
    )

    hypotheses: Mapped[list["SecurityHypothesis"]] = relationship(
        secondary="hypothesis_observations",
        back_populates="observations",
    )
from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base



class FindingObservation(Base):
    __tablename__ = "finding_observations"

    # Candidate.
    finding_candidate_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey(
            "finding_candidates.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    # Observation, подтверждающая candidate.
    observation_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey(
            "observations.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )


class FindingCandidate(Base):
    __tablename__ = "finding_candidates"

    # ID технического candidate.
    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Execution, в котором проблема обнаружена.
    execution_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Target, к которому относится candidate.
    target_snapshot_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("target_snapshots.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Название потенциальной проблемы.
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Техническое описание.
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Предварительная severity.
    severity: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    # Уверенность analysis.
    confidence: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    # Отпечаток для дедупликации.
    fingerprint: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    # detected / validated / rejected / promoted
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="detected",
        index=True,
    )

    # Когда candidate создан.
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    execution: Mapped["Execution"] = relationship(
        back_populates="finding_candidates",
    )

    observations: Mapped[list["Observation"]] = relationship(
        secondary="finding_observations",
        back_populates="finding_candidates",
    )


    hypothesis_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey(
            "security_hypotheses.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    validation_run_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey(
            "validation_runs.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    hypothesis: Mapped["SecurityHypothesis | None"] = relationship()

    validation_run: Mapped["ValidationRun | None"] = relationship()




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
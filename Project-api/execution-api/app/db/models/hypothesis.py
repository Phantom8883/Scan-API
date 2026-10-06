from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class HypothesisObservation(Base):
    """
    Связующая таблица между SecurityHypothesis и Observation.

    Одна гипотеза может основываться на нескольких наблюдениях,
    и одно наблюдение может использоваться несколькими гипотезами.
    """

    __tablename__ = "hypothesis_observations"

    # Гипотеза.
    hypothesis_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey(
            "security_hypotheses.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    # Наблюдение, на котором основана гипотеза.
    observation_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey(
            "observations.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )


class SecurityHypothesis(Base):
    """
    Предположение анализа о потенциальной security-проблеме.

    Это ещё НЕ подтверждённая уязвимость.
    """

    __tablename__ = "security_hypotheses"

    # ID гипотезы.
    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Execution, в рамках которого появилась гипотеза.
    execution_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey(
            "executions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # Target, к которому относится гипотеза.
    target_snapshot_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey(
            "target_snapshots.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # Категория, например:
    # A01:2025
    # A05:2025
    # A07:2025
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    # Краткое название гипотезы.
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Почему analysis считает гипотезу возможной.
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Уверенность analysis в гипотезе.
    #
    # Например:
    # 0.87 = 87%
    confidence: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    # proposed
    # testing
    # validated
    # rejected
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="proposed",
        index=True,
    )

    # Когда гипотеза создана.
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    # Связь с execution.
    execution: Mapped["Execution"] = relationship(
        back_populates="hypotheses",
    )

    # Наблюдения, на которых основана гипотеза.
    observations: Mapped[list["Observation"]] = relationship(
        secondary="hypothesis_observations",
        back_populates="hypotheses",
    )

    # План проверки.
    plans: Mapped[list["ValidationPlan"]] = relationship(
        back_populates="hypothesis",
        cascade="all, delete-orphan",
    )
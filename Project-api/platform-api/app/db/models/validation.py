from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, JSON, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ValidationPlan(Base):
    """
    Структурированный план проверки SecurityHypothesis.

    Analysis создаёт его, Validation Engine исполняет.
    """

    __tablename__ = "validation_plans"

    # ID плана.
    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Гипотеза, которую проверяем.
    hypothesis_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey(
            "security_hypotheses.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # Цель проверки.
    objective: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Входные данные, необходимые validation engine.
    input_data: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # Как должен вести себя безопасный вариант системы.
    expected_secure_behavior: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Как может выглядеть небезопасное поведение.
    expected_insecure_behavior: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Формализованные критерии успешной проверки.
    success_criteria: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # Дополнительные ограничения проверки.
    constraints: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # proposed
    # approved
    # running
    # completed
    # rejected
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="proposed",
        index=True,
    )

    # Когда план создан.
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    hypothesis: Mapped["SecurityHypothesis"] = relationship(
        back_populates="plans",
    )

    runs: Mapped[list["ValidationRun"]] = relationship(
        back_populates="plan",
        cascade="all, delete-orphan",
    )


class ValidationRun(Base):
    """
    Конкретное выполнение ValidationPlan.

    Именно эта сущность отражает фактическую попытку проверки.
    """

    __tablename__ = "validation_runs"

    # ID конкретного запуска проверки.
    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # План, который выполняем.
    plan_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey(
            "validation_plans.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # Execution, в котором проходит проверка.
    execution_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey(
            "executions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # Job Celery, отвечающий за эту проверку.
    job_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey(
            "jobs.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # queued
    # running
    # completed
    # failed
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="queued",
        index=True,
    )

    # Когда проверка началась.
    started_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    # Когда проверка закончилась.
    finished_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    plan: Mapped["ValidationPlan"] = relationship(
        back_populates="runs",
    )

    execution: Mapped["Execution"] = relationship()

    job: Mapped["Job | None"] = relationship()

    result: Mapped["ValidationResult | None"] = relationship(
        back_populates="run",
        uselist=False,
        cascade="all, delete-orphan",
    )


class ValidationResult(Base):
    """
    Результат фактической security-проверки.

    Здесь фиксируем не просто success=True/False,
    а что произошло во время проверки.
    """

    __tablename__ = "validation_results"

    # ID результата.
    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Конкретный ValidationRun.
    run_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey(
            "validation_runs.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    # Удалось ли подтвердить гипотезу.
    success: Mapped[bool] = mapped_column(
        nullable=False,
    )

    # Уверенность в результате проверки.
    confidence: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    # Что было до проверки.
    baseline: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # Что было получено во время/после проверки.
    observed_state: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # Какие изменения были обнаружены.
    observed_changes: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # Какая информация была потенциально раскрыта.
    data_exposure: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # Изменилось ли состояние системы.
    state_changed: Mapped[bool | None] = mapped_column(
        nullable=True,
    )

    # Дополнительный текстовый вывод.
    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    run: Mapped["ValidationRun"] = relationship(
        back_populates="result",
    )
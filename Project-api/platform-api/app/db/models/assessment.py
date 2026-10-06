from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, JSON, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Assessment(Base):
    __tablename__ = "assessments"

    # ID assessment.
    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Проект, который проверяем.
    project_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Пользователь, создавший assessment.
    created_by_user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # Состояние:
    # draft / ready / running / completed / failed
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="draft",
        index=True,
    )

    # Настройки assessment.
    #
    # Позже здесь будут выбранные security modules,
    # ограничения и прочая configuration.
    configuration: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # Когда assessment создан.
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    project: Mapped["Project"] = relationship(
        back_populates="assessments",
    )

    created_by_user: Mapped["User"] = relationship(
        back_populates="assessments",
    )

    targets: Mapped[list["AssessmentTarget"]] = relationship(
        back_populates="assessment",
        cascade="all, delete-orphan",
    )

    findings: Mapped[list["Finding"]] = relationship(
        back_populates="assessment",
        cascade="all, delete-orphan",
    )

    reports: Mapped[list["Report"]] = relationship(
        back_populates="assessment",
        cascade="all, delete-orphan",
    )


class AssessmentTarget(Base):
    __tablename__ = "assessment_targets"

    # Assessment.
    assessment_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Target.
    target_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("targets.id", ondelete="CASCADE"),
        primary_key=True,
    )

    assessment: Mapped["Assessment"] = relationship(
        back_populates="targets",
    )

    target: Mapped["Target"] = relationship()
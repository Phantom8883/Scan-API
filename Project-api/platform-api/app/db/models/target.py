from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Target(Base):
    __tablename__ = "targets"

    # ID target.
    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Проект, которому принадлежит target.
    project_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Исходное значение:
    # example.com
    # 192.168.1.10
    # https://example.com
    value: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Тип:
    # domain / ip / url / network
    target_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Нормализованное значение.
    normalized_value: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Состояние target.
    #
    # pending / verified / disabled
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        index=True,
    )

    # Когда target добавлен.
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    project: Mapped["Project"] = relationship(
        back_populates="targets",
    )

    verifications: Mapped[list["TargetVerification"]] = relationship(
        back_populates="target",
        cascade="all, delete-orphan",
    )


class TargetVerification(Base):
    __tablename__ = "target_verifications"

    # ID проверки.
    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Target, который проверяем.
    target_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("targets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Тип проверки:
    # dns / http / manual
    verification_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Прошла ли проверка.
    verified: Mapped[bool] = mapped_column(
        nullable=False,
    )

    # Когда проверка произведена.
    verified_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    target: Mapped["Target"] = relationship(
        back_populates="verifications",
    )
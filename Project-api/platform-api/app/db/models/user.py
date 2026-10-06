from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    # Уникальный ID пользователя.
    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Имя пользователя.
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Email для входа.
    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True,
    )

    # Хэш пароля.
    # Сам пароль никогда не сохраняется.
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Позволяет отключить пользователя.
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    # Когда пользователь создан.
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    # Организации пользователя.
    memberships: Mapped[list["OrganizationMembership"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # Созданные пользователем assessments.
    assessments: Mapped[list["Assessment"]] = relationship(
        back_populates="created_by_user",
    )
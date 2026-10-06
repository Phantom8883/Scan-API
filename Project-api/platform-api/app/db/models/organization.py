from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    # ID организации.
    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Название организации.
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    # Когда организация создана.
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    # Участники организации.
    memberships: Mapped[list["OrganizationMembership"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    # Проекты организации.
    projects: Mapped[list["Project"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
    )


class OrganizationMembership(Base):
    __tablename__ = "organization_memberships"

    # ID пользователя.
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # ID организации.
    organization_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Роль пользователя.
    #
    # owner / admin / member
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="member",
    )

    user: Mapped["User"] = relationship(
        back_populates="memberships",
    )

    organization: Mapped["Organization"] = relationship(
        back_populates="memberships",
    )
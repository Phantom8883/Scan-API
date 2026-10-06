from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Project(Base):
    __tablename__ = "projects"

    # ID проекта.
    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Организация-владелец.
    organization_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Название проекта.
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    # Когда проект создан.
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    organization: Mapped["Organization"] = relationship(
        back_populates="projects",
    )

    targets: Mapped[list["Target"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )

    assessments: Mapped[list["Assessment"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
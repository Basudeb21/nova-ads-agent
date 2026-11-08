from datetime import datetime

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Index,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.mysql import CHAR, DATETIME
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Project(Base):

    __tablename__ = "projects"

    __table_args__ = (
        Index("idx_project_status", "status"),
        Index("idx_project_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    project_id: Mapped[str] = mapped_column(
        CHAR(36),
        nullable=False,
        unique=True,
    )

    project_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    product_image_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    image_format: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    image_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="CREATED",
    )

    created_at: Mapped[datetime] = mapped_column(
        DATETIME(fsp=6),
        nullable=False,
        server_default=func.current_timestamp(6),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DATETIME(fsp=6),
        nullable=False,
        server_default=func.current_timestamp(6),
        server_onupdate=func.current_timestamp(6),
    )


class ProjectRequirementRecord(Base):

    __tablename__ = "project_requirements"

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            name="uq_project_requirements_project",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    project_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey(
            "projects.project_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    schema_version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    requirements_json: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    requirements_text_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    confirmed_at: Mapped[datetime] = mapped_column(
        DATETIME(fsp=6),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DATETIME(fsp=6),
        nullable=False,
        server_default=func.current_timestamp(6),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DATETIME(fsp=6),
        nullable=False,
        server_default=func.current_timestamp(6),
        server_onupdate=func.current_timestamp(6),
    )
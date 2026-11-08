
from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    Index,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.mysql import BIGINT, CHAR, DATETIME
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class AgentExecution(Base):

    __tablename__ = "agent_execution_logs"

    __table_args__ = (
        Index("idx_execution_agent", "agent_code", "arrival_at"),
        Index("idx_execution_project", "project_id"),
        Index("idx_execution_status", "status", "arrival_at"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    execution_id: Mapped[str] = mapped_column(
        CHAR(36),
        nullable=False,
        unique=True,
    )

    agent_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    project_id: Mapped[str | None] = mapped_column(
        CHAR(36),
        nullable=True,
    )

    execution_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="STARTED",
    )

    arrival_at: Mapped[datetime] = mapped_column(
        DATETIME(fsp=6),
        nullable=False,
        server_default=func.current_timestamp(6),
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DATETIME(fsp=6),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DATETIME(fsp=6),
        nullable=True,
    )

    process_time_ms: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    execution_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
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

from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    String,
    Text,
    Integer,
    Boolean,
    JSON,
    DateTime,
    func,
)

from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Agent(Base):

    __tablename__ = "agent"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    agent_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    agent_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    display_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    agent_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    technology: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    responsibilities: Mapped[Any | None] = mapped_column(
        JSON,
        nullable=True,
    )

    execution_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.requirements.requirements import ProjectRequirements


class IntakeMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["user", "assistant", "system"]

    content: str = Field(min_length=1)

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class IntakeAsset(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    asset_type: Literal[
        "product_image",
        "brand_logo",
        "reference_image",
    ]

    original_filename: str

    file_path: str | None = None

    upload_status: Literal[
        "pending",
        "ready",
        "failed",
    ] = "pending"


class IntakeSessionState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: UUID = Field(
        default_factory=uuid4
    )

    content_type: str = Field(
        default="advertising",
        min_length=1,
    )

    module_version: str = Field(
        default="1.0",
        min_length=1,
    )

    status: Literal[
        "COLLECTING",
        "AWAITING_CONFIRMATION",
        "CONFIRMED",
        "CANCELLED",
    ] = "COLLECTING"

    requirements: ProjectRequirements = Field(
        default_factory=ProjectRequirements
    )

    assets: list[IntakeAsset] = Field(
        default_factory=list
    )

    messages: list[IntakeMessage] = Field(
        default_factory=list
    )

    pending_field: str | None = None

    pending_question: str | None = None

        # Question progression tracking
    current_question_id: str | None = None

    answered_question_ids: list[str] = Field(
        default_factory=list
    )

    skipped_question_ids: list[str] = Field(
        default_factory=list
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    last_activity_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
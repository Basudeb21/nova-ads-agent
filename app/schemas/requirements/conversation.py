
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class GeneratedQuestion(BaseModel):
    """
    Natural-language question generated from a fixed catalog entry.
    """

    model_config = ConfigDict(extra="forbid")

    question_id: str = Field(min_length=1)

    message: str = Field(min_length=1)

    examples: list[str] = Field(default_factory=list)

    allow_skip: bool = False


class ExtractedAnswer(BaseModel):
    """
    Structured interpretation of a user's response.
    """

    model_config = ConfigDict(extra="forbid")

    question_id: str = Field(min_length=1)

    status: Literal[
        "ANSWERED",
        "NEEDS_CLARIFICATION",
        "SKIPPED",
    ]

    extracted_values: dict[str, Any] = Field(
        default_factory=dict,
    )

    clarification_message: str | None = None

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    @model_validator(mode="after")
    def validate_extraction(self):

        if (
            self.status == "NEEDS_CLARIFICATION"
            and not self.clarification_message
        ):
            raise ValueError(
                "Clarification message is required."
            )

        if (
            self.status == "SKIPPED"
            and self.extracted_values
        ):
            raise ValueError(
                "Skipped answers cannot contain extracted values."
            )

        if (
            self.status == "ANSWERED"
            and not self.extracted_values
        ):
            raise ValueError(
                "Answered responses must contain extracted values."
            )

        return self


class ConversationTurnResponse(BaseModel):
    """
    Standard response returned by an intake conversation engine.
    """

    model_config = ConfigDict(extra="forbid")

    session_id: str

    question_id: str

    message: str

    conversation_status: Literal[
        "COLLECTING",
        "AWAITING_CONFIRMATION",
        "CONFIRMED",
        "CANCELLED",
    ]

    requires_user_response: bool = True

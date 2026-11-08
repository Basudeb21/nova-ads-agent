from pydantic import BaseModel, ConfigDict, Field


class ProjectDetails(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    project_name: str | None = Field(
        default=None,
        max_length=150,
    )

    purpose: str | None = None
    category: str | None = None
    description: str | None = None

    creative_variations: int = Field(
        default=1,
        ge=1,
        le=20,
    )
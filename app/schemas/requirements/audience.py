from pydantic import BaseModel, ConfigDict, Field


class TargetAudience(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    age_group: list[str] = Field(default_factory=list)

    gender_preference: str | None = None

    locations: list[str] = Field(default_factory=list)

    interests: list[str] = Field(default_factory=list)

    customer_type: str | None = None

    description: str | None = None
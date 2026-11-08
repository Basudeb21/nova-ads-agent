from pydantic import BaseModel, ConfigDict, Field


class CreativeDirection(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    visual_style: str | None = None

    preferred_colors: list[str] = Field(
        default_factory=list,
    )

    avoid_colors: list[str] = Field(
        default_factory=list,
    )

    mood: str | None = None

    background_preference: str | None = None

    composition_preference: str | None = None

    reference_description: str | None = None
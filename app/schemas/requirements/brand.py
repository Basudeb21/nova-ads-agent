from pydantic import BaseModel, ConfigDict, Field


class BrandInformation(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    logo_required: bool = False

    logo_path: str | None = None

    brand_name: str | None = None

    brand_guidelines: str | None = None

    font_preferences: list[str] = Field(
        default_factory=list,
    )

    reference_images: list[str] = Field(
        default_factory=list,
    )
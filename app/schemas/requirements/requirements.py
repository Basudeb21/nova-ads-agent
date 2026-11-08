from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from app.services.dimensions import dimensions_loader

from app.schemas.requirements.project import ProjectDetails
from app.schemas.requirements.audience import TargetAudience
from app.schemas.requirements.creative import CreativeDirection
from app.schemas.requirements.content import AdvertisementContent
from app.schemas.requirements.brand import BrandInformation


class PlacementSelection(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    platform: str

    placement: str

    dimension_id: str | None = None

    width: int | None = None

    height: int | None = None

    aspect_ratio: str | None = None

    formats: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def resolve_dimensions(self):

        self.platform = self.platform.lower()
        self.placement = self.placement.lower()

        try:
            details = dimensions_loader.get_placement(
                platform=self.platform,
                placement=self.placement,
            )

        except ValueError as exc:
            raise ValueError(str(exc)) from exc

        self.dimension_id = details["dimension_id"]
        self.width = details["width"]
        self.height = details["height"]
        self.aspect_ratio = details.get("aspect_ratio")
        self.formats = details.get("format", [])

        return self


class RequirementsValidation(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    is_complete: bool = False

    missing_fields: list[str] = Field(
        default_factory=list,
    )

    confirmed_by_user: bool = False


class ProjectRequirements(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    schema_version: str = "1.0"

    project: ProjectDetails = Field(
        default_factory=ProjectDetails,
    )

    placements: list[PlacementSelection] = Field(
        default_factory=list,
    )

    audience: TargetAudience = Field(
        default_factory=TargetAudience,
    )

    creative_direction: CreativeDirection = Field(
        default_factory=CreativeDirection,
    )

    advertisement_content: AdvertisementContent = Field(
        default_factory=AdvertisementContent,
    )

    brand: BrandInformation = Field(
        default_factory=BrandInformation,
    )

    additional_instructions: list[str] = Field(
        default_factory=list,
    )

    validation: RequirementsValidation = Field(
        default_factory=RequirementsValidation,
    )
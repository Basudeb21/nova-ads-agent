from pydantic import BaseModel, ConfigDict, Field

from app.schemas.requirements.intake import (
    IntakeSessionState,
)


class IntakeProgress(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_complete: bool = False

    missing_fields: list[str] = Field(
        default_factory=list
    )

    completed_fields: list[str] = Field(
        default_factory=list
    )

    completion_percentage: float = 0.0


def evaluate_intake_progress(
    state: IntakeSessionState,
) -> IntakeProgress:

    missing = []
    completed = []

    requirements = state.requirements

    # --------------------------------------------------
    # 1. Product image
    # --------------------------------------------------

    product_image_ready = any(
        asset.asset_type == "product_image"
        and asset.upload_status == "ready"
        and asset.file_path
        for asset in state.assets
    )

    if product_image_ready:
        completed.append("product_image")
    else:
        missing.append("product_image")

    # --------------------------------------------------
    # 2. Project name
    # --------------------------------------------------

    if requirements.project.project_name:
        completed.append("project.project_name")
    else:
        missing.append("project.project_name")

    # --------------------------------------------------
    # 3. Advertisement placement
    # --------------------------------------------------

    if requirements.placements:
        completed.append("placements")
    else:
        missing.append("placements")

    # --------------------------------------------------
    # 4. Visual style
    # --------------------------------------------------

    if requirements.creative_direction.visual_style:
        completed.append("creative_direction.visual_style")
    else:
        missing.append("creative_direction.visual_style")

    # --------------------------------------------------
    # 5. Brand logo, if required
    # --------------------------------------------------

    if requirements.brand.logo_required:

        logo_ready = any(
            asset.asset_type == "brand_logo"
            and asset.upload_status == "ready"
            and asset.file_path
            for asset in state.assets
        )

        if logo_ready:
            completed.append("brand.logo")
        else:
            missing.append("brand.logo")

    # --------------------------------------------------
    # 6. Calculate progress
    # --------------------------------------------------

    total_fields = len(missing) + len(completed)

    percentage = (
        len(completed) / total_fields * 100
        if total_fields
        else 100.0
    )

    is_complete = len(missing) == 0

    # Update the requirements validation section.

    requirements.validation.is_complete = is_complete

    requirements.validation.missing_fields = missing

    return IntakeProgress(
        is_complete=is_complete,
        missing_fields=missing,
        completed_fields=completed,
        completion_percentage=round(percentage, 2),
    )
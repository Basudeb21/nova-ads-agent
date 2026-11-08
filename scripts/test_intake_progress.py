import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.schemas.requirements import (
    IntakeSessionState,
    IntakeAsset,
)

from app.agents.requirements_analysis.progress import (
    evaluate_intake_progress,
)


def main():

    print("\n========================================")
    print("  RIYA INTAKE PROGRESS TEST")
    print("========================================")

    # --------------------------------------
    # Test 1: Incomplete session
    # --------------------------------------

    state = IntakeSessionState()

    print("\nSession ID:", state.session_id)

    progress = evaluate_intake_progress(state)

    print("\nTest 1: Incomplete Session")
    print("Complete:", progress.is_complete)
    print("Progress:", progress.completion_percentage, "%")
    print("Missing:", progress.missing_fields)

    assert progress.is_complete is False

    # --------------------------------------
    # Test 2: Complete required information
    # --------------------------------------

    state.requirements.project.project_name = (
        "Summer Product Campaign"
    )

    state.requirements.placements.append(
        {
            "platform": "instagram",
            "placement": "story",
        }
    )

    state.requirements.creative_direction.visual_style = (
        "Premium and modern"
    )

    state.assets.append(
        IntakeAsset(
            asset_type="product_image",
            original_filename="product.png",
            file_path="storage/test/product.png",
            upload_status="ready",
        )
    )

    progress = evaluate_intake_progress(state)

    print("\nTest 2: Complete Required Information")
    print("Complete:", progress.is_complete)
    print("Progress:", progress.completion_percentage, "%")
    print("Completed:", progress.completed_fields)
    print("Missing:", progress.missing_fields)

    assert progress.is_complete is True
    assert len(progress.missing_fields) == 0

    # --------------------------------------
    # Test 3: Logo requirement
    # --------------------------------------

    state.requirements.brand.logo_required = True

    progress = evaluate_intake_progress(state)

    print("\nTest 3: Logo Required But Not Uploaded")
    print("Complete:", progress.is_complete)
    print("Missing:", progress.missing_fields)

    assert progress.is_complete is False
    assert "brand.logo" in progress.missing_fields

    print("\nINTAKE PROGRESS TEST SUCCESSFUL")


if __name__ == "__main__":
    main()
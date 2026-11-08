
import base64

from pathlib import Path

from sqlalchemy import select

from app.agents.requirements_analysis.review import (
    RequirementsReviewService,
)
from app.database.connection import SessionLocal
from app.database.models.project import (
    Project,
    ProjectRequirementRecord,
)
from app.schemas.requirements.intake import (
    IntakeAsset,
    IntakeSessionState,
)
from app.schemas.requirements.requirements import (
    PlacementSelection,
)
from app.services.storage.intake_session_repository import (
    IntakeSessionRepository,
)


def test_invalid_confirmation():
    state = IntakeSessionState()
    session_id = str(state.session_id)

    IntakeSessionRepository.create_session(state)

    try:
        try:
            RequirementsReviewService.confirm(session_id)
            raise AssertionError(
                "Incomplete requirements were confirmed."
            )
        except RuntimeError:
            print("Incomplete confirmation rejected: PASS")

        def set_review_status(current):
            current.status = "AWAITING_CONFIRMATION"

        IntakeSessionRepository.update_session(
            session_id,
            set_review_status,
        )

        try:
            RequirementsReviewService.confirm(session_id)
            raise AssertionError(
                "Invalid requirements were confirmed."
            )
        except ValueError:
            print("Validation before confirmation: PASS")

    finally:
        IntakeSessionRepository.delete_session(session_id)


def test_confirm_and_create_project():
    image_path = Path("storage/input/riya_handoff_test.png")
    image_path.parent.mkdir(parents=True, exist_ok=True)

    image_path.write_bytes(
        base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/"
            "l6sAAAAASUVORK5CYII="
        )
    )

    state = IntakeSessionState()
    session_id = str(state.session_id)

    state.status = "AWAITING_CONFIRMATION"
    state.requirements.project.project_name = (
        "Riya Niladittya Handoff Test"
    )

    state.requirements.placements.append(
        PlacementSelection(
            platform="instagram",
            placement="story",
        )
    )

    state.requirements.creative_direction.visual_style = "Modern"

    state.assets.append(
        IntakeAsset(
            asset_type="product_image",
            original_filename=image_path.name,
            file_path=str(image_path.resolve()),
            upload_status="ready",
        )
    )

    IntakeSessionRepository.create_session(state)

    try:
        confirmed = RequirementsReviewService.confirm(
            session_id
        )

        assert confirmed.status == "CONFIRMED"
        assert confirmed.requirements.validation.confirmed_by_user
        assert image_path.exists() is False

        project_message = confirmed.messages[-1].content

        assert "Project ID:" in project_message

        project_id = project_message.split(
            "Project ID:", 1
        )[1].splitlines()[0].strip()

        db = SessionLocal()

        try:
            project = db.scalar(
                select(Project).where(
                    Project.project_id == project_id
                )
            )

            requirements = db.scalar(
                select(ProjectRequirementRecord).where(
                    ProjectRequirementRecord.project_id == project_id
                )
            )

            assert project is not None
            assert requirements is not None
            assert Path(project.product_image_path).is_file()

        finally:
            db.close()

        print("Riya confirmation: PASS")
        print("Automatic Niladittya handoff: PASS")
        print("Project database registration: PASS")
        print("Requirements database registration: PASS")
        print("Product image transfer: PASS")
        print(f"Created project: {project_id}")

    finally:
        IntakeSessionRepository.delete_session(session_id)


if __name__ == "__main__":
    test_invalid_confirmation()
    test_confirm_and_create_project()

    print("\nRIYA → NILADITTYA INTEGRATION SUCCESSFUL")

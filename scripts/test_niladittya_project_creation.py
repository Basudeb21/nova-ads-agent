
import base64
from pathlib import Path

from sqlalchemy import select

from app.database.connection import SessionLocal
from app.database.models.agent import Agent
from app.database.models.project import (
    Project,
    ProjectRequirementRecord,
)
from app.agents.orchestrators.workflow_orchestrator.agent import (
    WorkflowOrchestrator,
)
from app.schemas.requirements.intake import (
    IntakeSessionState,
    IntakeAsset,
)
from app.schemas.requirements.requirements import (
    ProjectRequirements,
)


def main():
    db = SessionLocal()
    image_path = Path("storage/input/niladittya_test.png")

    try:
        # 1. Load Niladittya's database configuration.
        agent_config = db.scalar(
            select(Agent).where(
                Agent.agent_code == "1001"
            )
        )

        if agent_config is None:
            raise RuntimeError(
                "Niladittya not found in agent table."
            )

        # 2. Initialize Niladittya.
        agent = WorkflowOrchestrator(agent_config)
        agent.initialize()

        # 3. Create a temporary test product image.
        image_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        image_path.write_bytes(
            base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/"
                "l6sAAAAASUVORK5CYII="
            )
        )

        # 4. Prepare confirmed requirements.
        requirements = ProjectRequirements(
            project={
                "project_name": "Niladittya Integration Test",
            },
            placements=[
                {
                    "platform": "instagram",
                    "placement": "feed_square",
                }
            ],
            creative_direction={
                "visual_style": "Modern",
            },
            validation={
                "is_complete": True,
                "confirmed_by_user": True,
            },
        )

        # 5. Prepare confirmed intake session.
        intake_state = IntakeSessionState(
            status="CONFIRMED",
            requirements=requirements,
            assets=[
                IntakeAsset(
                    asset_type="product_image",
                    original_filename=image_path.name,
                    file_path=str(image_path.resolve()),
                    upload_status="ready",
                )
            ],
        )

        # 6. Execute Niladittya's project creation.
        result = agent.create_project(intake_state)

        print("\nPROJECT CREATION RESULT")
        print("=" * 45)

        for key, value in result.items():
            print(f"{key}: {value}")

        # 7. Verify committed records using a fresh session.
        db.close()
        db = SessionLocal()

        project = db.scalar(
            select(Project).where(
                Project.project_id == result["project_id"]
            )
        )

        requirement_record = db.scalar(
            select(ProjectRequirementRecord).where(
                ProjectRequirementRecord.project_id
                == result["project_id"]
            )
        )

        assert project is not None, (
            "Project record was not found in MySQL."
        )

        assert requirement_record is not None, (
            "Project requirements were not found in MySQL."
        )

        product_file = Path(project.product_image_path)

        assert product_file.is_file(), (
            f"Product image not found: {product_file}"
        )

        requirements_file = Path(
            requirement_record.requirements_text_path
        )

        assert requirements_file.is_file(), (
            f"Requirements file not found: {requirements_file}"
        )

        print("\n" + "=" * 45)
        print("PROJECT DATABASE: PASSED")
        print("REQUIREMENTS DATABASE: PASSED")
        print("PRODUCT IMAGE MOVEMENT: PASSED")
        print("REQUIREMENTS FILE: PASSED")
        print("=" * 45)

    finally:
        db.close()


if __name__ == "__main__":
    main()

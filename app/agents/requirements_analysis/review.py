
from typing import Any

from app.agents.requirements_analysis.progress import (
    evaluate_intake_progress,
)
from app.agents.orchestrators.workflow_orchestrator.agent import (
    WorkflowOrchestrator,
)
from app.database.connection import SessionLocal
from app.database.models.agent import Agent
from app.schemas.requirements.intake import (
    IntakeMessage,
    IntakeSessionState,
)
from app.services.storage.intake_session_repository import (
    IntakeSessionRepository,
)


class RequirementsReviewService:

    @staticmethod
    def validate(state: IntakeSessionState) -> dict[str, Any]:
        progress = evaluate_intake_progress(state)

        return {
            "is_complete": progress.is_complete,
            "missing_fields": progress.missing_fields,
            "completed_fields": progress.completed_fields,
            "completion_percentage": progress.completion_percentage,
        }

    @staticmethod
    def generate_summary(state: IntakeSessionState) -> str:
        requirements = state.requirements

        lines = [
            "NOVA ADS STUDIO - PROJECT REQUIREMENTS",
            "=" * 45,
            "",
            f"Project: {requirements.project.project_name or 'Not provided'}",
            "",
            "AD PLACEMENTS",
            "-" * 20,
        ]

        if requirements.placements:
            for placement in requirements.placements:
                lines.append(
                    f"- {placement.platform.title()} / "
                    f"{placement.placement}: "
                    f"{placement.width}x{placement.height}"
                )
        else:
            lines.append("- Not provided")

        lines.extend([
            "",
            "TARGET AUDIENCE",
            "-" * 20,
            str(requirements.audience.model_dump()),
            "",
            "CREATIVE DIRECTION",
            "-" * 20,
            str(requirements.creative_direction.model_dump()),
            "",
            "ADVERTISEMENT CONTENT",
            "-" * 20,
            str(requirements.advertisement_content.model_dump()),
            "",
            "BRAND INFORMATION",
            "-" * 20,
            str(requirements.brand.model_dump()),
            "",
            "ADDITIONAL INSTRUCTIONS",
            "-" * 20,
            *(
                [f"- {item}" for item in requirements.additional_instructions]
                or ["- None"]
            ),
            "",
            "VALIDATION",
            "-" * 20,
        ])

        validation = RequirementsReviewService.validate(state)

        lines.append(
            f"Completion: {validation['completion_percentage']}%"
        )
        lines.append(
            f"Ready for confirmation: {validation['is_complete']}"
        )

        if validation["missing_fields"]:
            lines.append("Missing requirements:")
            lines.extend(
                f"- {field}" for field in validation["missing_fields"]
            )

        return "\n".join(lines)

    @staticmethod
    def _create_project(
        state: IntakeSessionState,
        orchestrator: WorkflowOrchestrator | None = None,
    ) -> dict:

        if orchestrator is not None:
            return orchestrator.create_project(state)

        db = SessionLocal()

        try:
            agent_config = db.query(Agent).filter(
                Agent.agent_code == "1001"
            ).one_or_none()

            if agent_config is None:
                raise RuntimeError(
                    "Niladittya (agent 1001) was not found."
                )

            orchestrator = WorkflowOrchestrator(agent_config)
            orchestrator.initialize()

            return orchestrator.create_project(state)

        finally:
            db.close()

    @staticmethod
    def confirm(
        session_id: str,
        orchestrator: WorkflowOrchestrator | None = None,
    ) -> IntakeSessionState:

        state = IntakeSessionRepository.get_session(session_id)

        if state is None:
            raise KeyError(
                f"Intake session not found: {session_id}"
            )

        # Accept either collecting or awaiting-confirmation sessions.
        if state.status not in {
            "COLLECTING",
            "AWAITING_CONFIRMATION",
        }:
            raise RuntimeError(
                f"Cannot confirm session with status: {state.status}"
            )

        # Always validate the actual requirements before confirmation.
        progress = evaluate_intake_progress(state)

        if not progress.is_complete:
            raise RuntimeError(
                f"Requirements are incomplete: {progress.missing_fields}"
            )

        def update(current):

            current_progress = evaluate_intake_progress(current)

            if not current_progress.is_complete:
                raise ValueError(
                    f"Requirements incomplete: "
                    f"{current_progress.missing_fields}"
                )

            if current.status not in {
                "COLLECTING",
                "AWAITING_CONFIRMATION",
            }:
                raise RuntimeError(
                    f"Cannot confirm session with status: {current.status}"
                )

            current.requirements.validation.confirmed_by_user = True
            current.requirements.validation.is_complete = True
            current.status = "CONFIRMED"

            current.messages.append(
                IntakeMessage(
                    role="assistant",
                    content=(
                        "Your project requirements have been confirmed."
                    ),
                )
            )

        confirmed_state = IntakeSessionRepository.update_session(
            session_id,
            update,
        )

        if confirmed_state is None:
            raise KeyError(
                f"Intake session not found: {session_id}"
            )

        # Hand confirmed requirements to Niladittya.
        project_result = RequirementsReviewService._create_project(
            confirmed_state,
            orchestrator=orchestrator,
        )

        def add_project_result(current):
            current.messages.append(
                IntakeMessage(
                    role="assistant",
                    content=(
                        "Your project has been created successfully.\n"
                        f"Project ID: {project_result['project_id']}\n"
                        f"Project Name: {project_result['project_name']}"
                    ),
                )
            )

        final_state = IntakeSessionRepository.update_session(
            session_id,
            add_project_result,
        )

        if final_state is None:
            raise KeyError(
                f"Intake session not found: {session_id}"
            )

        return final_state

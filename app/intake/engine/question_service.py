
from typing import Any

from app.agents.requirements_analysis.progress import IntakeProgress
from app.agents.requirements_analysis.progress import evaluate_intake_progress
from app.intake.engine.question_manager import QuestionManager
from app.schemas.requirements.intake import IntakeSessionState
from app.services.storage.intake_session_repository import (
    IntakeSessionRepository,
)


class QuestionService:
    """
    Coordinates question progression with Redis-backed sessions.

    Answer validation remains the responsibility of the
    module-specific validator.
    """

    def __init__(
        self,
        question_manager: QuestionManager | None = None,
    ) -> None:
        self.question_manager = (
            question_manager or QuestionManager()
        )

    def get_next_question(
        self,
        session_id: str,
    ) -> dict[str, Any] | None:

        selected_question: dict[str, Any] | None = None

        def update(state: IntakeSessionState) -> None:
            nonlocal selected_question

            question = self.question_manager.get_next_question(
                state
            )

            selected_question = (
                dict(question) if question is not None else None
            )

        updated_state = IntakeSessionRepository.update_session(
            session_id,
            update,
        )

        if updated_state is None:
            raise KeyError(f"Intake session not found: {session_id}")

        return selected_question

    def mark_answered(
        self,
        session_id: str,
        question_id: str,
    ) -> IntakeSessionState:

        def update(state: IntakeSessionState) -> None:
            self.question_manager.mark_answered(
                state,
                question_id,
            )

        updated_state = IntakeSessionRepository.update_session(
            session_id,
            update,
        )

        if updated_state is None:
            raise KeyError(f"Intake session not found: {session_id}")

        return updated_state

    def mark_skipped(
        self,
        session_id: str,
        question_id: str,
    ) -> IntakeSessionState:

        def update(state: IntakeSessionState) -> None:
            self.question_manager.mark_skipped(
                state,
                question_id,
            )

        updated_state = IntakeSessionRepository.update_session(
            session_id,
            update,
        )

        if updated_state is None:
            raise KeyError(f"Intake session not found: {session_id}")

        return updated_state

    def get_session(
        self,
        session_id: str,
    ) -> IntakeSessionState | None:
        return IntakeSessionRepository.get_session(session_id)

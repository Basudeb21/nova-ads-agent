
from typing import Any

from app.intake.engine.catalog_registry import (
    IntakeCatalogRegistry,
    intake_catalog_registry,
)
from app.schemas.requirements.intake import IntakeSessionState


class QuestionManager:
    """
    Universal question progression manager.

    Does not contain advertising-specific logic.
    Question selection is controlled by the registered module catalog.
    """

    def __init__(
        self,
        registry: IntakeCatalogRegistry | None = None,
    ) -> None:
        self.registry = registry or intake_catalog_registry

    def _get_questions(
        self,
        state: IntakeSessionState,
    ) -> tuple[dict[str, Any], ...]:
        module = self.registry.get_module(
            content_type=state.content_type,
            version=state.module_version,
        )

        return module.questions

    def _get_question(
        self,
        state: IntakeSessionState,
        question_id: str,
    ) -> dict[str, Any]:
        questions = self._get_questions(state)

        for question in questions:
            if question["question_id"] == question_id:
                return question

        raise ValueError(
            f"Question '{question_id}' does not exist in "
            f"module '{state.content_type}' "
            f"version '{state.module_version}'."
        )

    def get_next_question(
        self,
        state: IntakeSessionState,
    ) -> dict[str, Any] | None:
        """
        Return the next unanswered question.

        Repeated calls return the same question until it is
        answered or an optional question is skipped.
        """

        if state.status != "COLLECTING":
            return None

        questions = sorted(
            self._get_questions(state),
            key=lambda question: question["order"],
        )

        # Preserve the current question if it is still pending.
        if state.current_question_id is not None:
            current = self._get_question(
                state,
                state.current_question_id,
            )

            if (
                state.current_question_id
                not in state.answered_question_ids
                and state.current_question_id
                not in state.skipped_question_ids
            ):
                return current

            state.current_question_id = None

        answered = set(state.answered_question_ids)
        skipped = set(state.skipped_question_ids)

        for question in questions:
            question_id = question["question_id"]

            if question_id in answered or question_id in skipped:
                continue

            state.current_question_id = question_id
            return question

        return None

    def mark_answered(
        self,
        state: IntakeSessionState,
        question_id: str,
    ) -> None:
        """
        Mark a question as answered after module-specific
        answer validation has succeeded.
        """

        self._get_question(state, question_id)

        if question_id in state.answered_question_ids:
            return

        if state.current_question_id != question_id:
            raise ValueError(
                "Only the current question can be marked as answered."
            )

        if question_id in state.skipped_question_ids:
            state.skipped_question_ids.remove(question_id)

        state.answered_question_ids.append(question_id)
        state.current_question_id = None

    def mark_skipped(
        self,
        state: IntakeSessionState,
        question_id: str,
    ) -> None:
        """
        Skip an optional question.

        Mandatory questions cannot be skipped.
        """

        question = self._get_question(state, question_id)

        if question.get("required", False):
            raise ValueError(
                f"Mandatory question '{question_id}' cannot be skipped."
            )

        if question_id in state.answered_question_ids:
            raise ValueError(
                f"Answered question '{question_id}' cannot be skipped."
            )

        if question_id in state.skipped_question_ids:
            return

        if state.current_question_id != question_id:
            raise ValueError(
                "Only the current question can be skipped."
            )

        state.skipped_question_ids.append(question_id)
        state.current_question_id = None

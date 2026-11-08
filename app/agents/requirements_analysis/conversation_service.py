from typing import Any

from app.agents.requirements_analysis.progress import (
    evaluate_intake_progress,
)
from app.core.logging import get_logger
from app.intake.engine.answer_applier import AnswerApplier
from app.intake.engine.answer_extractor import AnswerExtractor
from app.intake.engine.question_generator import QuestionGenerator
from app.intake.engine.question_service import QuestionService
from app.schemas.requirements.conversation import (
    ConversationTurnResponse,
)
from app.schemas.requirements.intake import IntakeMessage
from app.services.storage.intake_session_repository import (
    IntakeSessionRepository,
)

logger = get_logger("nova.riya.conversation")


class RiyaConversationService:

    def __init__(
        self,
        question_service: QuestionService | None = None,
        question_generator: QuestionGenerator | None = None,
        answer_extractor: AnswerExtractor | None = None,
        answer_applier: AnswerApplier | None = None,
    ) -> None:
        self.question_service = question_service or QuestionService()
        self.question_generator = question_generator or QuestionGenerator()
        self.answer_extractor = answer_extractor or AnswerExtractor()
        self.answer_applier = answer_applier or AnswerApplier()

    async def get_next_turn(
        self,
        session_id: str,
    ) -> ConversationTurnResponse | None:

        question = self.question_service.get_next_question(session_id)

        if question is None:
            state = self.question_service.get_session(session_id)

            if state is None:
                raise KeyError(f"Intake session not found: {session_id}")

            progress = evaluate_intake_progress(state)

            if not progress.is_complete:
                if progress.missing_fields == ["brand.logo"]:
                    return None

                logger.warning(
                    "Intake incomplete for %s. Missing: %s",
                    session_id,
                    progress.missing_fields,
                )
                raise RuntimeError(
                    f"Requirements incomplete: {progress.missing_fields}"
                )

            def complete_session(current_state) -> None:
                current_state.status = "AWAITING_CONFIRMATION"

            IntakeSessionRepository.update_session(
                session_id,
                complete_session,
            )
            return None

        state = self.question_service.get_session(session_id)

        if state is None:
            raise KeyError(f"Intake session not found: {session_id}")

        question_id = question["question_id"]

        if (
            state.current_question_id == question_id
            and state.pending_question
        ):
            return ConversationTurnResponse(
                session_id=session_id,
                question_id=question_id,
                message=state.pending_question,
                conversation_status=state.status,
            )

        conversation_history = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in state.messages
        ]

        generated = await self.question_generator.generate(
            question=question,
            conversation_history=conversation_history,
        )

        def update_session(current_state) -> None:
            if current_state.status != "COLLECTING":
                raise RuntimeError(
                    "Cannot generate questions for a session "
                    "that is not collecting requirements."
                )

            current_state.current_question_id = question_id
            current_state.pending_question = generated.message

            current_state.messages.append(
                IntakeMessage(
                    role="assistant",
                    content=generated.message,
                )
            )

        updated_state = IntakeSessionRepository.update_session(
            session_id,
            update_session,
        )

        if updated_state is None:
            raise KeyError(f"Intake session not found: {session_id}")

        logger.info(
            "Riya generated question %s for session %s",
            question_id,
            session_id,
        )

        return ConversationTurnResponse(
            session_id=session_id,
            question_id=question_id,
            message=generated.message,
            conversation_status=updated_state.status,
        )

    async def submit_answer(
        self,
        session_id: str,
        user_answer: str,
    ) -> ConversationTurnResponse | None:

        if not user_answer or not user_answer.strip():
            raise ValueError("User answer cannot be empty.")

        state = self.question_service.get_session(session_id)

        if state is None:
            raise KeyError(f"Intake session not found: {session_id}")

        if state.status != "COLLECTING":
            raise RuntimeError(
                f"Cannot submit answers when session status is {state.status}."
            )

        if not state.current_question_id:
            raise RuntimeError("There is no active question to answer.")

        question = self.question_service.get_next_question(session_id)

        if question is None:
            raise RuntimeError("No pending question is available.")

        question_id = state.current_question_id

        if question["question_id"] != question_id:
            raise RuntimeError("Active question does not match session state.")

        conversation_history = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in state.messages
        ]

        extracted = await self.answer_extractor.extract(
            question=question,
            user_answer=user_answer.strip(),
            conversation_history=conversation_history,
        )

        def update_session(current_state) -> None:
            if current_state.status != "COLLECTING":
                raise RuntimeError("Intake session is no longer collecting.")

            if current_state.current_question_id != question_id:
                raise RuntimeError("The active question has changed.")

            current_state.messages.append(
                IntakeMessage(
                    role="user",
                    content=user_answer.strip(),
                )
            )

            if extracted.status == "NEEDS_CLARIFICATION":
                current_state.pending_question = (
                    extracted.clarification_message
                )

                current_state.messages.append(
                    IntakeMessage(
                        role="assistant",
                        content=extracted.clarification_message,
                    )
                )

                return

            if extracted.status == "SKIPPED":
                self.question_service.question_manager.mark_skipped(
                    current_state,
                    question_id,
                )

                current_state.pending_question = None
                return

            if extracted.status == "ANSWERED":
                current_state.requirements = self.answer_applier.apply(
                    current_state.requirements,
                    extracted.extracted_values,
                )

                self.question_service.question_manager.mark_answered(
                    current_state,
                    question_id,
                )

                current_state.pending_question = None

                if current_state.content_type == "advertising":
                    evaluate_intake_progress(current_state)

        updated_state = IntakeSessionRepository.update_session(
            session_id,
            update_session,
        )

        if updated_state is None:
            raise KeyError(f"Intake session not found: {session_id}")

        logger.info(
            "Riya processed answer for question %s: %s",
            question_id,
            extracted.status,
        )

        if extracted.status == "NEEDS_CLARIFICATION":
            return ConversationTurnResponse(
                session_id=session_id,
                question_id=question_id,
                message=extracted.clarification_message,
                conversation_status=updated_state.status,
            )

        return await self.get_next_turn(session_id)

    def confirm_requirements(self, session_id: str):
        state = self.question_service.get_session(session_id)

        if state is None:
            raise KeyError(f"Intake session not found: {session_id}")

        if state.status != "AWAITING_CONFIRMATION":
            raise RuntimeError(
                "Requirements are not ready for confirmation."
            )

        progress = evaluate_intake_progress(state)

        if not progress.is_complete:
            raise ValueError(
                f"Requirements incomplete: {progress.missing_fields}"
            )

        def confirm(current_state):
            current_progress = evaluate_intake_progress(current_state)

            if not current_progress.is_complete:
                raise ValueError(
                    f"Requirements incomplete: "
                    f"{current_progress.missing_fields}"
                )

            current_state.status = "CONFIRMED"
            current_state.messages.append(
                IntakeMessage(
                    role="assistant",
                    content="Your project requirements have been confirmed.",
                )
            )

        updated = IntakeSessionRepository.update_session(
            session_id,
            confirm,
        )

        if updated is None:
            raise KeyError(f"Intake session not found: {session_id}")

        logger.info("Requirements confirmed for session %s", session_id)
        return updated
import asyncio

from app.intake.modules.register import register_builtin_modules
from app.agents.requirements_analysis.conversation_service import (
    RiyaConversationService,
)
from app.schemas.requirements.conversation import (
    ExtractedAnswer,
    GeneratedQuestion,
)
from app.schemas.requirements.intake import IntakeSessionState
from app.services.storage.intake_session_repository import (
    IntakeSessionRepository,
)


class FakeQuestionGenerator:

    async def generate(self, question, conversation_history=None):
        return GeneratedQuestion(
            question_id=question["question_id"],
            message=f"Test question: {question['question_id']}?",
            allow_skip=not question["required"],
        )


class FakeAnswerExtractor:

    def __init__(self):
        self.responses = [
            ExtractedAnswer(
                question_id="project_name",
                status="NEEDS_CLARIFICATION",
                clarification_message="Could you provide a more specific project name?",
            ),
            ExtractedAnswer(
                question_id="project_name",
                status="ANSWERED",
                extracted_values={
                    "project.project_name": "Summer Sale 2026"
                },
            ),
            ExtractedAnswer(
                question_id="campaign_purpose",
                status="SKIPPED",
            ),
        ]

    async def extract(self, **kwargs):
        return self.responses.pop(0)


async def main():
    register_builtin_modules()

    state = IntakeSessionState()
    session_id = str(state.session_id)

    IntakeSessionRepository.create_session(state)

    service = RiyaConversationService(
        question_generator=FakeQuestionGenerator(),
        answer_extractor=FakeAnswerExtractor(),
    )

    # 1. Initial question
    first = await service.get_next_turn(session_id)
    assert first.question_id == "project_name"

    # 2. Clarification
    clarification = await service.submit_answer(
        session_id,
        "Summer",
    )
    assert "specific project name" in clarification.message
    print("Clarification handling: PASS")

    # 3. Answer after clarification
    next_turn = await service.submit_answer(
        session_id,
        "Summer Sale 2026",
    )

    saved = service.question_service.get_session(session_id)

    assert saved.requirements.project.project_name == "Summer Sale 2026"
    assert next_turn.question_id == "campaign_purpose"
    print("Answer application: PASS")

    # 4. Optional question skip
    next_turn = await service.submit_answer(
        session_id,
        "Skip",
    )

    saved = service.question_service.get_session(session_id)

    assert "campaign_purpose" in saved.skipped_question_ids
    assert next_turn.question_id == "target_audience"
    print("Optional question skip: PASS")

    IntakeSessionRepository.delete_session(session_id)

    print("=" * 50)
    print("RIYA EDGE CASE TESTS SUCCESSFUL")


if __name__ == "__main__":
    asyncio.run(main())
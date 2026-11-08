import asyncio

from app.intake.modules.register import register_builtin_modules
from app.schemas.requirements.intake import IntakeSessionState
from app.services.storage.intake_session_repository import (
    IntakeSessionRepository,
)
from app.agents.requirements_analysis.conversation_service import (
    RiyaConversationService,
)


async def main():
    print("=" * 60)
    print("NOVA - RIYA ANSWER SUBMISSION TEST")
    print("=" * 60)

    register_builtin_modules()

    state = IntakeSessionState()
    IntakeSessionRepository.create_session(state)

    service = RiyaConversationService()

    first_turn = await service.get_next_turn(str(state.session_id))
    print("Question:", first_turn.message)

    next_turn = await service.submit_answer(
        str(state.session_id),
        "Summer Sale 2026",
    )

    updated_state = service.question_service.get_session(
        str(state.session_id)
    )

    assert updated_state.requirements.project.project_name == (
        "Summer Sale 2026"
    )

    print("Project name:", updated_state.requirements.project.project_name)
    print("Answer persisted: SUCCESS")

    if next_turn:
        print("Next question:", next_turn.message)

    print("=" * 60)
    print("RIYA ANSWER SUBMISSION TEST SUCCESSFUL")


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.intake.modules.register import register_builtin_modules
from app.schemas.requirements.intake import IntakeSessionState
from app.services.storage.intake_session_repository import (
    IntakeSessionRepository,
)
from app.agents.requirements_analysis.conversation_service import (
    RiyaConversationService,
)


async def main():

    register_builtin_modules()

    state = IntakeSessionState()

    created = IntakeSessionRepository.create_session(state)

    assert created is True

    service = RiyaConversationService()

    try:
        print("=" * 60)
        print("NOVA - RIYA CONVERSATION SERVICE TEST")
        print("=" * 60)

        # Generate first question.
        first_turn = await service.get_next_turn(
            str(state.session_id)
        )

        assert first_turn is not None
        assert first_turn.question_id == "project_name"
        assert first_turn.message

        print("First question:", first_turn.message)

        # Verify the generated question is persisted.
        saved_state = service.question_service.get_session(
            str(state.session_id)
        )

        assert saved_state is not None
        assert saved_state.pending_question == first_turn.message
        assert saved_state.current_question_id == "project_name"

        print("Question persisted: SUCCESS")

        # Calling again must reuse the pending question.
        second_turn = await service.get_next_turn(
            str(state.session_id)
        )

        assert second_turn is not None
        assert second_turn.message == first_turn.message

        print("Pending question reuse: SUCCESS")

        print("=" * 60)
        print("RIYA CONVERSATION SERVICE TEST SUCCESSFUL")
        print("=" * 60)

    finally:
        IntakeSessionRepository.delete_session(
            state.session_id
        )


if __name__ == "__main__":
    asyncio.run(main())

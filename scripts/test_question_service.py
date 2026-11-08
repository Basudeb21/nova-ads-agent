import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.intake.modules.register import register_builtin_modules
from app.schemas.requirements.intake import IntakeSessionState
from app.services.storage.intake_session_repository import (
    IntakeSessionRepository,
)
from app.intake.engine.question_service import QuestionService

def main():

    print("=" * 60)
    print("NOVA - REDIS QUESTION SERVICE TEST")
    print("=" * 60)
    register_builtin_modules()
    service = QuestionService()

    session = IntakeSessionState(
        content_type="advertising",
        module_version="1.0",
    )

    session_id = str(session.session_id)

    try:
        # 1. Create session
        assert IntakeSessionRepository.create_session(session)

        print("1. Redis session creation: SUCCESS")

        # 2. Retrieve first question
        first_question = service.get_next_question(session_id)

        assert first_question is not None
        assert first_question["order"] == 1

        print("2. First question retrieval: SUCCESS")

        # 3. Verify current question persistence
        repeated_question = service.get_next_question(session_id)

        assert (
            repeated_question["question_id"]
            == first_question["question_id"]
        )

        print("3. Current question persistence: SUCCESS")

        # 4. Mark first question answered
        service.mark_answered(
            session_id,
            first_question["question_id"],
        )

        print("4. Answer progression: SUCCESS")

        # 5. Retrieve second question
        second_question = service.get_next_question(session_id)

        assert second_question is not None
        assert second_question["order"] > first_question["order"]

        print("5. Next question retrieval: SUCCESS")

        # 6. Verify Redis persistence
        restored_session = service.get_session(session_id)

        assert restored_session is not None

        assert (
            first_question["question_id"]
            in restored_session.answered_question_ids
        )

        assert (
            restored_session.current_question_id
            == second_question["question_id"]
        )

        print("6. Redis progression persistence: SUCCESS")

        # 7. Mandatory question protection
        placements_question = None

        # Advance to the required placements question.
        for _ in range(10):
            current = service.get_next_question(session_id)

            if current is None:
                break

            if current["required"]:
                placements_question = current
                break

            service.mark_skipped(
                session_id,
                current["question_id"],
            )

        assert placements_question is not None

        try:
            service.mark_skipped(
                session_id,
                placements_question["question_id"],
            )
        except ValueError:
            pass
        else:
            raise AssertionError(
                "Mandatory question was incorrectly skipped."
            )

        print("7. Mandatory question protection: SUCCESS")

        # 8. Cleanup
        assert IntakeSessionRepository.delete_session(session_id)

        print("8. Redis test cleanup: SUCCESS")

        print("=" * 60)
        print("REDIS QUESTION SERVICE TEST SUCCESSFUL")
        print("=" * 60)

    finally:
        IntakeSessionRepository.delete_session(session_id)


if __name__ == "__main__":
    main()

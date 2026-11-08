import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.schemas.requirements.conversation import (
    GeneratedQuestion,
    ExtractedAnswer,
    ConversationTurnResponse,
)


def main() -> None:
    print("=" * 60)
    print("NOVA - CONVERSATION SCHEMA TEST")
    print("=" * 60)

    question = GeneratedQuestion(
        question_id="project_name",
        message="What would you like to name your campaign?",
        allow_skip=False,
    )
    assert question.question_id == "project_name"
    print("1. Generated question: SUCCESS")

    answer = ExtractedAnswer(
        question_id="project_name",
        status="ANSWERED",
        extracted_values={
            "project.project_name": "Summer Campaign",
        },
        confidence=0.98,
    )
    assert answer.status == "ANSWERED"
    print("2. Answer extraction: SUCCESS")

    clarification = ExtractedAnswer(
        question_id="placements",
        status="NEEDS_CLARIFICATION",
        clarification_message=(
            "Which Instagram placement do you mean?"
        ),
    )
    assert clarification.clarification_message
    print("3. Clarification response: SUCCESS")

    skipped = ExtractedAnswer(
        question_id="campaign_purpose",
        status="SKIPPED",
    )
    assert skipped.status == "SKIPPED"
    print("4. Optional skip: SUCCESS")

    response = ConversationTurnResponse(
        session_id="test-session",
        question_id="project_name",
        message="What would you like to name your campaign?",
        conversation_status="COLLECTING",
    )
    assert response.requires_user_response
    print("5. Conversation response: SUCCESS")

    print("=" * 60)
    print("CONVERSATION SCHEMA TEST SUCCESSFUL")
    print("=" * 60)


if __name__ == "__main__":
    main()

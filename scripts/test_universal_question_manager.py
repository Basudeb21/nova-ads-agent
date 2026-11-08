import sys
from pathlib import Path

# Add project root to Python import path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.intake.engine.catalog_registry import (
    IntakeCatalogRegistry,
    IntakeModuleDefinition,
)
from app.intake.modules.advertising.module import ADVERTISING_MODULE
from app.intake.engine.question_manager import QuestionManager
from app.schemas.requirements.intake import IntakeSessionState


def create_test_registry():
    registry = IntakeCatalogRegistry()

    # Register the existing advertising module.
    registry.register(ADVERTISING_MODULE)

    # Simulate a future hiring module.
    hiring_module = IntakeModuleDefinition(
        content_type="hiring",
        version="2.0",
        display_name="Hiring Requirements",
        description="Collects requirements for recruitment advertisements.",
        questions=(
            {
                "question_id": "job_title",
                "order": 1,
                "field": "job_title",
                "required": True,
            },
            {
                "question_id": "job_location",
                "order": 2,
                "field": "job_location",
                "required": True,
            },
            {
                "question_id": "salary_range",
                "order": 3,
                "field": "salary_range",
                "required": False,
            },
        ),
    )

    registry.register(hiring_module)

    return registry


def main():
    print("=" * 60)
    print("NOVA - UNIVERSAL QUESTION MANAGER TEST")
    print("=" * 60)

    registry = create_test_registry()
    manager = QuestionManager(registry)

    # ---------------------------------------------------------
    # TEST 1: Advertising module question retrieval
    # ---------------------------------------------------------

    advertising_session = IntakeSessionState(
        content_type="advertising",
        module_version="1.0",
    )

    first_question = manager.get_next_question(
        advertising_session
    )

    assert first_question is not None
    assert first_question["order"] == 1

    print("1. Advertising question retrieval: SUCCESS")

    # ---------------------------------------------------------
    # TEST 2: Question order
    # ---------------------------------------------------------

    current_question = manager.get_next_question(
        advertising_session
    )

    assert current_question["question_id"] == first_question["question_id"]

    manager.mark_answered(
        advertising_session,
        first_question["question_id"],
    )

    second_question = manager.get_next_question(
        advertising_session
    )

    assert second_question is not None
    assert second_question["order"] > first_question["order"]

    print("2. Fixed question ordering: SUCCESS")

    # ---------------------------------------------------------
    # TEST 3: Current question persistence
    # ---------------------------------------------------------

    repeated_question = manager.get_next_question(
        advertising_session
    )

    assert (
        repeated_question["question_id"]
        == second_question["question_id"]
    )

    print("3. Current question persistence: SUCCESS")


    
    # ---------------------------------------------------------
    # TEST 4: Mandatory question cannot be skipped
    # ---------------------------------------------------------

    mandatory_test_session = IntakeSessionState(
        content_type="advertising",
        module_version="1.0",
    )

    mandatory_question = manager.get_next_question(
        mandatory_test_session
    )

    assert mandatory_question["required"] is True

    try:
        manager.mark_skipped(
            mandatory_test_session,
            mandatory_question["question_id"],
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Mandatory question was incorrectly skipped."
        )

    assert (
        mandatory_test_session.current_question_id
        == mandatory_question["question_id"]
    )

    print("4. Mandatory question protection: SUCCESS")

    
    # ---------------------------------------------------------
    # TEST 5: Optional question skipping
    # ---------------------------------------------------------

    hiring_session = IntakeSessionState(
        content_type="hiring",
        module_version="2.0",
    )

    job_title = manager.get_next_question(hiring_session)

    assert job_title["question_id"] == "job_title"

    manager.mark_answered(
        hiring_session,
        "job_title",
    )

    job_location = manager.get_next_question(hiring_session)

    assert job_location["question_id"] == "job_location"

    manager.mark_answered(
        hiring_session,
        "job_location",
    )

    salary = manager.get_next_question(hiring_session)

    assert salary["question_id"] == "salary_range"
    assert salary["required"] is False

    manager.mark_skipped(
        hiring_session,
        "salary_range",
    )

    assert "salary_range" in hiring_session.skipped_question_ids

    print("5. Optional question skipping: SUCCESS")

    # ---------------------------------------------------------
    # TEST 6: Hiring module independence
    # ---------------------------------------------------------

    assert hiring_session.content_type == "hiring"
    assert advertising_session.content_type == "advertising"

    assert (
        hiring_session.answered_question_ids
        == ["job_title", "job_location"]
    )

    assert (
        advertising_session.answered_question_ids
        == [first_question["question_id"]]
    )

    print("6. Independent module progression: SUCCESS")

    # ---------------------------------------------------------
    # TEST 7: Completed module returns no question
    # ---------------------------------------------------------

    next_question = manager.get_next_question(
        hiring_session
    )

    assert next_question is None

    print("7. Completed question sequence: SUCCESS")

    # ---------------------------------------------------------
    # TEST 8: Unknown module protection
    # ---------------------------------------------------------

    unknown_session = IntakeSessionState(
        content_type="unknown",
        module_version="1.0",
    )

    try:
        manager.get_next_question(unknown_session)
    except KeyError:
        pass
    else:
        raise AssertionError(
            "Unknown module was incorrectly accepted."
        )

    print("8. Unknown module protection: SUCCESS")

    print("=" * 60)
    print("UNIVERSAL QUESTION MANAGER TEST SUCCESSFUL")
    print("=" * 60)


if __name__ == "__main__":
    main()

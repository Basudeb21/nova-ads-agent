
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from app.agents.requirements_analysis.question_catalog import (
    get_question_catalog,
    get_question_by_id,
    get_required_questions,
    get_question_sequence,
)


def main():

    print("=" * 55)
    print("RIYA - QUESTION CATALOG TEST")
    print("=" * 55)

    questions = get_question_catalog()

    assert len(questions) == 10
    print("1. Fixed question catalog: SUCCESS")

    required = get_required_questions()

    required_ids = {
        question["question_id"]
        for question in required
    }

    assert required_ids == {
        "project_name",
        "placements",
        "visual_style",
    }

    print("2. Required questions: SUCCESS")

    question = get_question_by_id("placements")

    assert question is not None
    assert question["field"] == "placements"

    print("3. Question lookup: SUCCESS")

    sequence = get_question_sequence()

    assert sequence[0] == "project_name"
    assert sequence[-1] == "additional_instructions"

    print("4. Fixed question sequence: SUCCESS")

    assert len(set(sequence)) == len(sequence)

    print("5. Unique question IDs: SUCCESS")

    print()
    print("QUESTION SEQUENCE:")

    for item in questions:
        requirement = (
            "REQUIRED" if item["required"] else "OPTIONAL"
        )

        print(
            f'{item["order"]}. '
            f'{item["question_id"]} [{requirement}]'
        )

    print("=" * 55)
    print("RIYA QUESTION CATALOG TEST SUCCESSFUL")
    print("=" * 55)


if __name__ == "__main__":
    main()


import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.agents.requirements_analysis.question_catalog import (
    get_question_by_id,
)
from app.intake.engine.question_generator import QuestionGenerator


async def main() -> None:
    print("=" * 60)
    print("NOVA - QUESTION GENERATOR TEST")
    print("=" * 60)

    generator = QuestionGenerator()

    question = get_question_by_id("project_name")

    assert question is not None

    result = await generator.generate(
        question=question,
        conversation_history=[],
    )

    print("Question ID:", result.question_id)
    print("Generated message:", result.message)
    print("Examples:", result.examples)
    print("Allow skip:", result.allow_skip)

    assert result.question_id == "project_name"
    assert result.message
    assert result.allow_skip is False

    print("\nQUESTION GENERATOR TEST SUCCESSFUL")


if __name__ == "__main__":
    asyncio.run(main())


import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.agents.requirements_analysis.question_catalog import (
    get_question_by_id,
)
from app.intake.engine.answer_extractor import AnswerExtractor


async def main():

    extractor = AnswerExtractor()

    question = get_question_by_id("project_name")

    result = await extractor.extract(
        question=question,
        user_answer="I want to call my campaign Summer Sale 2026.",
        conversation_history=[],
    )

    print("=" * 60)
    print("NOVA - RIYA ANSWER EXTRACTOR TEST")
    print("=" * 60)

    print("Question ID:", result.question_id)
    print("Status:", result.status)
    print("Extracted values:", result.extracted_values)
    print("Clarification:", result.clarification_message)
    print("Confidence:", result.confidence)

    assert result.question_id == "project_name"
    assert result.status == "ANSWERED"
    assert "project.project_name" in result.extracted_values

    print("=" * 60)
    print("ANSWER EXTRACTOR TEST SUCCESSFUL")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

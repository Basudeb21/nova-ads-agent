
import asyncio
import sys
from pathlib import Path

import httpx

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.agents.requirements_analysis.question_catalog import (
    get_question_by_id,
)


async def main():
    question = get_question_by_id("project_name")

    system_prompt = """
You are a professional conversational requirements analyst.

Convert a predefined question into natural conversational language.

Rules:
1. Ask only about the supplied intent.
2. Never invent user information.
3. Keep the question concise.
4. Provide up to three useful examples.

Return JSON exactly:
{
    "message": "Your conversational question",
    "examples": ["Example 1", "Example 2"]
}

Do not return question_id or allow_skip.
"""

    user_prompt = f"""
QUESTION INTENT:
{question.get("question_intent", "")}

QUESTION INSTRUCTIONS:
{question.get("llm_instructions", "")}

CONVERSATION HISTORY:
[]

Generate the conversational question.
"""

    payload = {
        "model": "qwen3.5:9b",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "format": "json",
        "think": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 512,
        },
    }

    async with httpx.AsyncClient(timeout=180.0) as client:
        response = await client.post(
            "http://127.0.0.1:11434/api/chat",
            json=payload,
        )
        response.raise_for_status()
        result = response.json()

    message = result.get("message", {})

    print("=" * 60)
    print("OLLAMA CHAT DIAGNOSTICS")
    print("=" * 60)

    print("Content:", repr(message.get("content")))
    print("Thinking:", repr(message.get("thinking")))
    print("Done:", result.get("done"))
    print("Done reason:", result.get("done_reason"))
    print("Evaluation count:", result.get("eval_count"))

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

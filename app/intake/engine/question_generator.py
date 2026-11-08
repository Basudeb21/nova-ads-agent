
from typing import Any

from app.core.logging import get_logger
from app.model_adapters.llm.ollama_adapter import OllamaAdapter
from app.schemas.requirements.conversation import GeneratedQuestion


logger = get_logger("nova.intake.question_generator")


class QuestionGenerator:
    """
    Converts fixed catalog questions into natural conversation.

    Question selection and mandatory rules remain controlled by Python.
    """

    def __init__(
        self,
        llm: OllamaAdapter | None = None,
    ) -> None:
        self.llm = llm or OllamaAdapter()

    async def generate(
        self,
        question: dict[str, Any],
        conversation_history: list[dict[str, str]] | None = None,
    ) -> GeneratedQuestion:

        question_id = question.get("question_id")

        if not question_id:
            raise ValueError(
                "Question catalog entry must contain question_id."
            )

        required = question.get("required", False)

        system_prompt = """
You are a professional conversational requirements analyst.

Your task is to convert a predefined question into natural,
friendly conversational language.

STRICT RULES:

1. Ask only about the supplied question intent.
2. Follow the supplied LLM instructions.
3. Never introduce a different question.
4. Never change the meaning of the question.
5. Never invent information about the user.
6. Avoid repeating information already clearly provided.
7. Use conversation history to maintain context.
8. Keep the message concise and natural.
9. Provide up to three useful examples when appropriate.

Return a JSON object with exactly these fields:

{
    "message": "Your conversational question",
    "examples": ["Example 1", "Example 2"]
}

Do not return question_id or allow_skip.
Python controls those values.
"""

        user_prompt = f"""
QUESTION INTENT:
{question.get("question_intent", "")}

QUESTION INSTRUCTIONS:
{question.get("llm_instructions", "")}

CONVERSATION HISTORY:
{conversation_history or []}

Generate the conversational question.
"""

        try:
            result = await self.llm.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3,
                max_tokens=512,
            )

            message = result.get("message")

            examples = result.get("examples", [])

            if not isinstance(message, str) or not message.strip():
                raise ValueError(
                    "LLM generated an empty question."
                )

            if not isinstance(examples, list):
                examples = []

            examples = [
                item.strip()
                for item in examples
                if isinstance(item, str) and item.strip()
            ][:3]

            generated_question = GeneratedQuestion(
                question_id=question_id,
                message=message.strip(),
                examples=examples,
                allow_skip=not required,
            )

            logger.info(
                "Question generated successfully: %s",
                question_id,
            )

            return generated_question

        except Exception:
            logger.exception(
                "Question generation failed: %s",
                question_id,
            )
            raise

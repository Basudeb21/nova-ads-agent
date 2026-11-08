import re
import json
from typing import Any

from app.core.logging import get_logger
from app.model_adapters.llm.ollama_adapter import OllamaAdapter
from app.schemas.requirements.conversation import ExtractedAnswer
from app.schemas.requirements.requirements import ProjectRequirements


logger = get_logger("nova.intake.answer_extractor")


class AnswerExtractor:

    def __init__(
        self,
        llm: OllamaAdapter | None = None,
    ) -> None:
        self.llm = llm or OllamaAdapter()

    @staticmethod
    def _resolve_schema(
        node: Any,
        definitions: dict[str, Any],
    ) -> Any:

        if isinstance(node, list):
            return [
                AnswerExtractor._resolve_schema(item, definitions)
                for item in node
            ]

        if not isinstance(node, dict):
            return node

        if "$ref" in node:
            reference = node["$ref"]
            definition_name = reference.split("/")[-1]

            if definition_name not in definitions:
                raise ValueError(
                    f"Unknown JSON schema reference: {reference}"
                )

            resolved = dict(definitions[definition_name])
            resolved.update({
                key: value
                for key, value in node.items()
                if key != "$ref"
            })

            return AnswerExtractor._resolve_schema(
                resolved,
                definitions,
            )

        return {
            key: AnswerExtractor._resolve_schema(value, definitions)
            for key, value in node.items()
        }

    @classmethod
    def _get_target_schema(
        cls,
        field_path: str,
    ) -> dict[str, Any]:

        root_schema = ProjectRequirements.model_json_schema()
        definitions = root_schema.get("$defs", {})
        current = root_schema

        for part in field_path.split("."):

            current = cls._resolve_schema(current, definitions)
            properties = current.get("properties", {})

            if part not in properties:
                raise ValueError(
                    f"Unknown requirement field: {field_path}"
                )

            current = properties[part]

        return cls._resolve_schema(current, definitions)



    @staticmethod
    def _normalize_value(
        value: Any,
        schema: dict[str, Any],
    ) -> Any:

        if not isinstance(schema, dict):
            return value

        if "anyOf" in schema:
            if value is None:
                return None

            schema = next(
                (
                    branch for branch in schema["anyOf"]
                    if branch.get("type") != "null"
                ),
                {},
            )

        expected_type = schema.get("type")

        if expected_type == "string" and isinstance(value, list):
            return ", ".join(str(item) for item in value)

        if expected_type == "array":

            item_schema = schema.get("items", {})

            # Convert natural-language lists into arrays.
            if isinstance(value, str):
                value = [
                    item.strip()
                    for item in re.split(
                        r"\s*(?:,|;|\band\b|&)\s*",
                        value,
                        flags=re.IGNORECASE,
                    )
                    if item.strip()
                ]

            if isinstance(value, list):
                return [
                    AnswerExtractor._normalize_value(item, item_schema)
                    for item in value
                ]

        if expected_type == "object" and isinstance(value, dict):
            properties = schema.get("properties", {})

            return {
                key: AnswerExtractor._normalize_value(
                    item,
                    properties[key],
                ) if key in properties else item
                for key, item in value.items()
            }

        return value






   
    @staticmethod
    def _normalize_response(
        result: dict[str, Any],
        target_field: str,
        target_schema: dict[str, Any],
        question_id: str,
    ) -> dict[str, Any]:

        if "extracted_values" not in result:
            if target_field in result:
                target_value = result[target_field]

            elif (
                target_schema.get("type") == "object"
                and set(result).intersection(
                    target_schema.get("properties", {})
                )
            ):
                # LLM returned the target object's properties directly.
                target_value = result

            else:
                return result

            result = {
                "question_id": question_id,
                "status": "ANSWERED",
                "extracted_values": {
                    target_field: target_value
                },
                "clarification_message": None,
                "confidence": 0.95,
            }

        values = result.get("extracted_values")

        if not isinstance(values, dict):
            return result

        if target_field not in values:
            if "target_field" in values:
                values = {
                    target_field: values["target_field"]
                }

            elif (
                target_schema.get("type") == "object"
                and set(values).intersection(
                    target_schema.get("properties", {})
                )
            ):
                values = {
                    target_field: values
                }

            else:
                return result

        result["question_id"] = result.get(
            "question_id", question_id
        )
        result["status"] = result.get("status", "ANSWERED")

        result["extracted_values"] = {
            target_field: AnswerExtractor._normalize_value(
                values[target_field],
                target_schema,
            )
        }

        result.setdefault("clarification_message", None)
        result.setdefault("confidence", 0.95)

        return result





   
    async def extract(
        self,
        question: dict[str, Any],
        user_answer: str,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> ExtractedAnswer:

        question_id = question.get("question_id")
        target_field = question.get("field")
        required = question.get("required", False)

        if not question_id or not target_field:
            raise ValueError("Invalid question definition.")

        if not user_answer.strip():
            raise ValueError("User answer cannot be empty.")

        target_schema = self._get_target_schema(target_field)

        system_prompt = """
You are Riya, a professional requirements analysis agent.

Extract the user's answer into structured JSON.

STRICT RULES:

1. Extract only information relevant to the supplied question.
2. Never invent or assume information.
3. Preserve the user's intended meaning.
4. Follow the supplied JSON schema strictly.
5. Nested models MUST be JSON objects.
6. Lists MUST be JSON arrays.
7. String fields MUST be JSON strings, never arrays.
8. Never convert objects or lists into strings.
9. If the answer is unclear or incomplete, use NEEDS_CLARIFICATION.
10. If the user explicitly declines an optional question, use SKIPPED.
11. Never skip a mandatory question.
12. Return JSON only.

RESPONSE STRUCTURE:

{
    "question_id": "actual question ID",
    "status": "ANSWERED",
    "extracted_values": {},
    "clarification_message": null,
    "confidence": 0.95
}

IMPORTANT:
- extracted_values MUST contain the exact target field as its key.
- Never use the literal key "target_field".
- The value must follow the expected JSON schema.
- Do not include unrelated fields.

Allowed statuses:
ANSWERED
NEEDS_CLARIFICATION
SKIPPED

For NEEDS_CLARIFICATION, provide clarification_message.
For SKIPPED, extracted_values must be empty.
Confidence must be between 0 and 1.
"""

        user_prompt = f"""
QUESTION ID:
{question_id}

TARGET FIELD:
{target_field}

EXPECTED JSON SCHEMA:
{json.dumps(target_schema, indent=2, ensure_ascii=False)}

MANDATORY:
{required}

QUESTION INTENT:
{question.get("question_intent", "")}

EXTRACTION INSTRUCTIONS:
{question.get("llm_instructions", "")}

CONVERSATION HISTORY:
{json.dumps(conversation_history or [], ensure_ascii=False)}

USER ANSWER:
{user_answer}

Return extracted_values using this exact key:
{json.dumps(target_field)}

Match every field's JSON type exactly.
"""

        result = await self.llm.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.1,
            max_tokens=1024,
        )

        if not isinstance(result, dict):
            raise ValueError("LLM returned an invalid JSON response.")

        result = self._normalize_response(
            result,
            target_field,
            target_schema,
            question_id,
        )

        extracted = ExtractedAnswer.model_validate(result)

        if extracted.question_id != question_id:
            raise ValueError("LLM returned an incorrect question ID.")

        if extracted.status == "SKIPPED" and required:
            raise ValueError("Mandatory questions cannot be skipped.")

        if (
            extracted.status == "ANSWERED"
            and target_field not in extracted.extracted_values
        ):
            raise ValueError(
                f"Extracted values must contain '{target_field}'."
            )

        logger.info(
            "Answer extracted: question=%s status=%s confidence=%.2f",
            question_id,
            extracted.status,
            extracted.confidence,
        )

        return extracted

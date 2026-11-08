
from __future__ import annotations

from copy import deepcopy
from typing import Any

from pydantic import ValidationError

from app.core.logging import get_logger
from app.schemas.requirements.requirements import ProjectRequirements

logger = get_logger("nova.intake.answer_applier")


class AnswerApplier:
    """Safely applies extracted answers to ProjectRequirements."""

    CONTENT_ALIASES = {
        "cta_text": "call_to_action",
        "tag_line": "tagline",
        "sub_headline": "subheadline",
    }

    def apply(
        self,
        requirements: ProjectRequirements,
        extracted_values: dict[str, Any],
    ) -> ProjectRequirements:
        if not extracted_values:
            raise ValueError("No extracted values provided.")

        data = requirements.model_dump(mode="python")

        for field_path, value in extracted_values.items():
            if not isinstance(field_path, str) or not field_path.strip():
                raise ValueError("Invalid extracted field path.")

            self._apply_value(data, field_path, value)

        self._normalize_advertisement_content(data)

        try:
            updated_requirements = ProjectRequirements.model_validate(data)
        except ValidationError:
            logger.exception("Extracted requirements validation failed.")
            raise

        logger.info(
            "Applied %s extracted requirement fields.",
            len(extracted_values),
        )

        return updated_requirements

    def _normalize_advertisement_content(
        self,
        data: dict[str, Any],
    ) -> None:
        content = data.get("advertisement_content")

        if not isinstance(content, dict):
            return

        for old_name, new_name in self.CONTENT_ALIASES.items():
            if old_name in content:
                value = content.pop(old_name)

                if new_name not in content:
                    content[new_name] = value

        # Convert simple LLM strings into CopyText objects.
        copy_fields = {
            "headline",
            "subheadline",
            "description",
            "slogan",
            "tagline",
            "call_to_action",
            "price",
            "offer",
            "promo_code",
            "disclaimer",
            "contact_information",
            "website",
        }

        for field in copy_fields:
            value = content.get(field)

            if isinstance(value, str) and value.strip():
                content[field] = {
                    "text": value.strip(),
                    "source": "user",
                    "must_preserve": True,
                    "confirmed": False,
                }

    def _apply_value(
        self,
        data: dict[str, Any],
        field_path: str,
        value: Any,
    ) -> None:
        parts = field_path.split(".")

        if any(not part for part in parts):
            raise ValueError(f"Invalid field path: {field_path}")

        current = data

        for part in parts[:-1]:
            if part not in current:
                raise ValueError(
                    f"Unknown requirement field: {field_path}"
                )

            nested = current[part]

            if not isinstance(nested, dict):
                raise ValueError(
                    f"Field path is not a valid nested object: {field_path}"
                )

            current = nested

        leaf = parts[-1]

        if leaf not in current:
            raise ValueError(
                f"Unknown requirement field: {field_path}"
            )

        existing_value = current[leaf]

        if isinstance(existing_value, dict) and isinstance(value, dict):
            merged = deepcopy(existing_value)
            merged.update(value)
            current[leaf] = merged
        else:
            current[leaf] = deepcopy(value)

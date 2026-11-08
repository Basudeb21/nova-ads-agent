
from dataclasses import dataclass
from typing import Any


# ============================================================
# INTAKE MODULE DEFINITION
# ============================================================

@dataclass(frozen=True)
class IntakeModuleDefinition:

    content_type: str
    version: str
    display_name: str
    description: str
    questions: tuple[dict[str, Any], ...]

    def __post_init__(self):

        if not self.content_type:
            raise ValueError("Content type cannot be empty.")

        if self.content_type != self.content_type.lower():
            raise ValueError(
                "Content type must use lowercase characters."
            )

        if not self.version:
            raise ValueError("Module version cannot be empty.")

        if not self.questions:
            raise ValueError(
                "An intake module must have a question catalog."
            )

        question_ids = [
            question["question_id"]
            for question in self.questions
        ]

        if len(question_ids) != len(set(question_ids)):
            raise ValueError(
                f"Duplicate question IDs in module: {self.content_type}"
            )

        question_orders = [
            question["order"]
            for question in self.questions
        ]

        if len(question_orders) != len(set(question_orders)):
            raise ValueError(
                f"Duplicate question orders in module: {self.content_type}"
            )


# ============================================================
# INTAKE CATALOG REGISTRY
# ============================================================

class IntakeCatalogRegistry:

    def __init__(self):

        self._modules: dict[
            tuple[str, str],
            IntakeModuleDefinition,
        ] = {}

        self._active_versions: dict[str, str] = {}

    # --------------------------------------------------------
    # REGISTER MODULE
    # --------------------------------------------------------

    def register(
        self,
        module: IntakeModuleDefinition,
        make_active: bool = True,
    ) -> None:

        key = (
            module.content_type,
            module.version,
        )

        if key in self._modules:
            raise ValueError(
                f"Module already registered: "
                f"{module.content_type} v{module.version}"
            )

        self._modules[key] = module

        if make_active:
            self._active_versions[module.content_type] = (
                module.version
            )

    # --------------------------------------------------------
    # GET MODULE
    # --------------------------------------------------------

    def get_module(
        self,
        content_type: str,
        version: str | None = None,
    ) -> IntakeModuleDefinition:

        if version is None:
            version = self._active_versions.get(content_type)

        if version is None:
            raise KeyError(
                f"No active intake module registered for: {content_type}"
            )

        key = (content_type, version)

        module = self._modules.get(key)

        if module is None:
            raise KeyError(
                f"Intake module not found: "
                f"{content_type} v{version}"
            )

        return module

    # --------------------------------------------------------
    # GET QUESTION CATALOG
    # --------------------------------------------------------

    def get_questions(
        self,
        content_type: str,
        version: str | None = None,
    ) -> tuple[dict[str, Any], ...]:

        module = self.get_module(
            content_type=content_type,
            version=version,
        )

        return module.questions

    # --------------------------------------------------------
    # CHECK REGISTRATION
    # --------------------------------------------------------

    def is_registered(
        self,
        content_type: str,
        version: str | None = None,
    ) -> bool:

        if version is None:
            return content_type in self._active_versions

        return (
            content_type,
            version,
        ) in self._modules

    # --------------------------------------------------------
    # LIST MODULES
    # --------------------------------------------------------

    def list_modules(self) -> list[dict[str, Any]]:

        result = []

        for (content_type, version), module in self._modules.items():

            result.append({
                "content_type": content_type,
                "version": version,
                "display_name": module.display_name,
                "description": module.description,
                "is_active": (
                    self._active_versions.get(content_type)
                    == version
                ),
                "question_count": len(module.questions),
            })

        return result


# ============================================================
# GLOBAL REGISTRY INSTANCE
# ============================================================

intake_catalog_registry = IntakeCatalogRegistry()

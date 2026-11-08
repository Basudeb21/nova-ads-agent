
from app.intake.engine.catalog_registry import (
    IntakeModuleDefinition,
)

from app.agents.requirements_analysis.question_catalog import (
    get_question_catalog,
)


ADVERTISING_MODULE = IntakeModuleDefinition(
    content_type="advertising",
    version="1.0",
    display_name="Advertising Requirements",
    description=(
        "Collects requirements for product advertisements, "
        "campaigns, promotional creatives, and advertising content."
    ),
    questions=get_question_catalog(),
)

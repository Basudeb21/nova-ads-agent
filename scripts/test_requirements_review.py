
from app.agents.requirements_analysis.review import (
    RequirementsReviewService,
)
from app.schemas.requirements.intake import IntakeSessionState


state = IntakeSessionState()

result = RequirementsReviewService.validate(state)
summary = RequirementsReviewService.generate_summary(state)

assert result["is_complete"] is False
assert result["missing_fields"]

print(summary)
print("\nREQUIREMENTS REVIEW TEST SUCCESSFUL")

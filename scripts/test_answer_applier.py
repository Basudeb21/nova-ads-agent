from app.intake.engine.answer_applier import AnswerApplier
from app.schemas.requirements.requirements import ProjectRequirements


def main():
    requirements = ProjectRequirements()

    applier = AnswerApplier()

    updated = applier.apply(
        requirements,
        {
            "project.project_name": "Summer Sale 2026",
        },
    )

    assert updated.project.project_name == "Summer Sale 2026"

    print("Project name:", updated.project.project_name)
    print("ANSWER APPLIER TEST SUCCESSFUL")


if __name__ == "__main__":
    main()
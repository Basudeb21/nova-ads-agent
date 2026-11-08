
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from app.intake.engine.catalog_registry import (
    IntakeCatalogRegistry,
    IntakeModuleDefinition,
    intake_catalog_registry,
)

from app.intake.modules.advertising.module import (
    ADVERTISING_MODULE,
)

from app.intake.modules.register import (
    register_builtin_modules,
)


def main():

    print("=" * 60)
    print("NOVA - UNIVERSAL INTAKE CATALOG REGISTRY TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. REGISTER BUILT-IN MODULES
    # --------------------------------------------------------

    register_builtin_modules()

    print("1. Built-in module registration: SUCCESS")

    # --------------------------------------------------------
    # 2. ADVERTISING MODULE LOOKUP
    # --------------------------------------------------------

    module = intake_catalog_registry.get_module(
        "advertising"
    )

    assert module.content_type == "advertising"
    assert module.version == "1.0"
    assert len(module.questions) == 10

    print("2. Advertising module lookup: SUCCESS")

    # --------------------------------------------------------
    # 3. QUESTION CATALOG LOOKUP
    # --------------------------------------------------------

    questions = intake_catalog_registry.get_questions(
        "advertising"
    )

    assert len(questions) == 10

    print("3. Module question retrieval: SUCCESS")

    # --------------------------------------------------------
    # 4. MODULE STATUS
    # --------------------------------------------------------

    assert intake_catalog_registry.is_registered(
        "advertising"
    )

    print("4. Module registration check: SUCCESS")

    # --------------------------------------------------------
    # 5. DUPLICATE PREVENTION
    # --------------------------------------------------------

    try:

        intake_catalog_registry.register(
            ADVERTISING_MODULE
        )

        raise AssertionError(
            "Duplicate module registration was accepted."
        )

    except ValueError:
        print("5. Duplicate registration prevention: SUCCESS")

    # --------------------------------------------------------
    # 6. FUTURE MODULE SIMULATION
    # --------------------------------------------------------

    test_registry = IntakeCatalogRegistry()

    hiring_module = IntakeModuleDefinition(
        content_type="hiring",
        version="2.0",
        display_name="Hiring Post Requirements",
        description="Collects requirements for recruitment posts.",
        questions=(
            {
                "question_id": "job_title",
                "order": 1,
                "field": "job_title",
                "required": True,
            },
            {
                "question_id": "job_location",
                "order": 2,
                "field": "job_location",
                "required": True,
            },
        ),
    )

    test_registry.register(hiring_module)

    registered_hiring = test_registry.get_module(
        "hiring"
    )

    assert registered_hiring.content_type == "hiring"
    assert len(registered_hiring.questions) == 2

    print("6. Future hiring module registration: SUCCESS")

    # --------------------------------------------------------
    # 7. MODULE INDEPENDENCE
    # --------------------------------------------------------

    assert test_registry.get_questions(
        "hiring"
    )[0]["question_id"] == "job_title"

    assert len(
        test_registry.get_questions("hiring")
    ) == 2

    print("7. Independent question catalogs: SUCCESS")

    # --------------------------------------------------------
    # 8. MODULE LIST
    # --------------------------------------------------------

    modules = intake_catalog_registry.list_modules()

    assert len(modules) >= 1

    print("8. Registered module listing: SUCCESS")

    print()
    print("REGISTERED MODULES:")

    for item in modules:

        print(
            f'{item["content_type"]} '
            f'v{item["version"]} '
            f'({item["question_count"]} questions)'
        )

    print("=" * 60)
    print("INTAKE CATALOG REGISTRY TEST SUCCESSFUL")
    print("=" * 60)


if __name__ == "__main__":
    main()

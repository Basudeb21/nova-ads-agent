
import subprocess
import sys

TESTS = [
    "scripts.test_conversation_schema",
    "scripts.test_requirements_schema",
    "scripts.test_riya_question_catalog",
    "scripts.test_intake_catalog_registry",
    "scripts.test_universal_question_manager",
    "scripts.test_intake_session_repository",
    "scripts.test_question_service",
    "scripts.test_question_generator",
    "scripts.test_answer_extractor",
    "scripts.test_answer_applier",
    "scripts.test_riya_conversation_service",
    "scripts.test_riya_answer_submission",
    "scripts.test_riya_edge_cases",
    "scripts.test_requirements_review",
    "scripts.test_riya_confirmation",
]

def main():
    print("=" * 65)
    print("NOVA ADS STUDIO - REQUIREMENT ANALYSIS TEST SUITE")
    print("=" * 65)

    failed = []

    for index, test in enumerate(TESTS, start=1):
        print(f"\n[{index}/{len(TESTS)}] Running {test}", flush=True)

        result = subprocess.run(
            [sys.executable, "-m", test],
            check=False,
        )

        if result.returncode != 0:
            failed.append(test)
            print(f"\nFAILED: {test}", flush=True)
            break

        print(f"PASSED: {test}", flush=True)

    print("\n" + "=" * 65)

    if failed:
        print("REQUIREMENT ANALYSIS SUITE FAILED")
        print("Failed test:", failed[0])
        sys.exit(1)

    print(f"ALL {len(TESTS)} TEST MODULES PASSED")
    print("REQUIREMENT ANALYSIS SUITE SUCCESSFUL")


if __name__ == "__main__":
    main()

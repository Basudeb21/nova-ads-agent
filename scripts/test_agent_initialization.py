import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from app.core.constants import ORCHESTRATOR_AGENT_CODE
from app.core.logging import setup_logging, get_logger
from app.database.connection import SessionLocal
from app.database.repositories.agent_repository import AgentRepository

from app.agents.orchestrators.workflow_orchestrator.agent import (
    WorkflowOrchestrator,
)


def main():

    setup_logging()

    logger = get_logger("nova.initialization")

    print()
    print("=" * 55)
    print("                 NOVA ADS STUDIO")
    print("=" * 55)

    db = SessionLocal()

    try:
        print("\nLoading orchestrator configuration...")

        agent_config = AgentRepository.get_by_code(
            db,
            ORCHESTRATOR_AGENT_CODE,
        )

        if agent_config is None:
            raise RuntimeError(
                "Workflow orchestrator configuration not found."
            )

        orchestrator = WorkflowOrchestrator(agent_config)

    finally:
        db.close()

    print("\nInitializing orchestrator...")

    orchestrator.initialize()

    logger.info(
        "Orchestrator initialization test successful."
    )

    print("NILADITTYA INITIALIZATION SUCCESSFUL")


if __name__ == "__main__":
    main()
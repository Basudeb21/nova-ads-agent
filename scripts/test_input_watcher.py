import sys
import time

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from app.core.logging import setup_logging
from app.agents.orchestrators.workflow_orchestrator.agent import (
    WorkflowOrchestrator,
)
from app.core.constants import ORCHESTRATOR_AGENT_CODE
from app.database.connection import SessionLocal
from app.database.repositories.agent_repository import AgentRepository

from app.services.storage.input_watcher import InputWatcher


def main():

    setup_logging()

    db = SessionLocal()

    try:
        agent_config = AgentRepository.get_by_code(
            db,
            ORCHESTRATOR_AGENT_CODE,
        )

        if agent_config is None:
            raise RuntimeError(
                "Orchestrator configuration not found."
            )

        orchestrator = WorkflowOrchestrator(agent_config)

    finally:
        db.close()

    orchestrator.initialize()

    watcher = InputWatcher()

    try:

        watcher.start()

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping input monitoring...")

    finally:
        watcher.stop()


if __name__ == "__main__":
    main()
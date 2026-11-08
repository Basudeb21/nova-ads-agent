
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.logging import setup_logging
from app.database.connection import SessionLocal
from app.database.repositories.agent_repository import AgentRepository
from app.agents.requirements_analysis import RequirementsAnalysisAgent


def main():

    setup_logging()

    db = SessionLocal()

    try:
        print("\nLoading Riya configuration...")

        config = AgentRepository.get_by_code(
            db=db,
            agent_code="1010",
        )

        if config is None:
            raise RuntimeError("Riya not found in database.")

        riya = RequirementsAnalysisAgent(config)

        print("\nInitializing Riya...")

        riya.initialize()

        print("RIYA INITIALIZATION SUCCESSFUL")

    finally:
        db.close()


if __name__ == "__main__":
    main()

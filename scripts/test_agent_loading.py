import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
from app.core.logging import setup_logging, get_logger

from app.database.connection import (
    SessionLocal,
    test_database_connection,
)

from app.database.repositories.agent_repository import AgentRepository


setup_logging()

logger = get_logger("nova.test")


def main():

    print("\n======================================")
    print("          NOVA ADS STUDIO")
    print("======================================")

    # Check database
    if not test_database_connection():
        raise RuntimeError("Database connection failed.")

    print("\n[DATABASE]")
    print("Connected successfully.")

    db = SessionLocal()

    try:

        print("\n[AGENT REGISTRY]")
        print("Loading NOVA...")

        agent = AgentRepository.get_by_code(db, "1001")

        if agent is None:
            raise RuntimeError(
                "NOVA agent not found or inactive."
            )

        print("\n[AGENT LOADED]")
        print(f"ID: {agent.id}")
        print(f"Code: {agent.agent_code}")
        print(f"Name: {agent.agent_name}")
        print(f"Display Name: {agent.display_name}")
        print(f"Type: {agent.agent_type}")
        print(f"Role: {agent.role}")
        print(f"Technology: {agent.technology}")
        print(f"Execution Order: {agent.execution_order}")
        print(f"Active: {agent.is_active}")

        logger.info("NOVA initialization test successful.")

        print("\n======================================")
        print("     NOVA LOADED SUCCESSFULLY")
        print("======================================")

    finally:
        db.close()


if __name__ == "__main__":
    main()
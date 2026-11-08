import sys
import time

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from app.core.logging import setup_logging
from app.database.connection import SessionLocal
from app.database.repositories.agent_execution_repository import (
    AgentExecutionRepository,
)


def main():

    setup_logging()

    db = SessionLocal()

    try:
        print("\n========================================")
        print("  AGENT EXECUTION TRACKING TEST")
        print("========================================")

        print("\nStarting Niladittya execution...")

        execution = AgentExecutionRepository.create_execution(
            db=db,
            agent_code="1001",
            execution_type="INITIALIZATION",
            project_id=None,
            execution_metadata={
                "agent_name": "Niladittya",
                "test": True,
                "source": "execution_tracking_test",
            },
        )

        print("\nExecution record created.")
        print(f"Execution ID: {execution.execution_id}")
        print(f"Agent Code: {execution.agent_code}")
        print(f"Status: {execution.status}")
        print(f"Arrival: {execution.arrival_at}")
        print(f"Started: {execution.started_at}")

        # Simulate a small amount of agent processing.
        process_start = time.perf_counter()
        time.sleep(0.5)

        process_time_ms = int(
            (time.perf_counter() - process_start) * 1000
        )

        finished = AgentExecutionRepository.finish_execution(
            db=db,
            execution_id=execution.execution_id,
            status="SUCCESS",
            process_time_ms=process_time_ms,
        )

        print("\nExecution completed.")
        print(f"Execution ID: {finished.execution_id}")
        print(f"Status: {finished.status}")
        print(f"Completed: {finished.completed_at}")
        print(f"Process Time: {finished.process_time_ms} ms")

        print("\nTRACKING TEST SUCCESSFUL")

    except Exception:
        print("\nTRACKING TEST FAILED.")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
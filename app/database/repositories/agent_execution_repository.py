import uuid

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.agent_execution import AgentExecution
from app.core.logging import get_logger


logger = get_logger("nova.repository.agent_execution")


class AgentExecutionRepository:

    VALID_STATUSES = {
        "STARTED",
        "SUCCESS",
        "FAILED",
        "CANCELLED",
    }

    @staticmethod
    def _utc_now() -> datetime:
        # MySQL DATETIME stores a timezone-naive value.
        return datetime.now(timezone.utc).replace(tzinfo=None)

    @staticmethod
    def create_execution(
        db: Session,
        agent_code: str,
        execution_type: str,
        project_id: str | None = None,
        execution_metadata: dict[str, Any] | None = None,
    ) -> AgentExecution:

        now = AgentExecutionRepository._utc_now()

        execution = AgentExecution(
            execution_id=str(uuid.uuid4()),
            agent_code=agent_code,
            project_id=project_id,
            execution_type=execution_type,
            status="STARTED",
            arrival_at=now,
            started_at=now,
            execution_metadata=execution_metadata,
        )

        try:
            db.add(execution)
            db.commit()
            db.refresh(execution)

            logger.info(
                "Agent execution started | Agent: %s | Execution: %s",
                agent_code,
                execution.execution_id,
            )

            return execution

        except Exception:
            db.rollback()

            logger.exception(
                "Failed to create agent execution | Agent: %s",
                agent_code,
            )

            raise

    @staticmethod
    def finish_execution(
        db: Session,
        execution_id: str,
        status: str,
        process_time_ms: int,
        error_message: str | None = None,
        execution_metadata: dict[str, Any] | None = None,
    ) -> AgentExecution:

        if status not in AgentExecutionRepository.VALID_STATUSES:
            raise ValueError(f"Invalid execution status: {status}")

        if status == "STARTED":
            raise ValueError(
                "finish_execution cannot set status to STARTED."
            )

        if process_time_ms < 0:
            raise ValueError("Processing time cannot be negative.")

        try:
            execution = db.scalar(
                select(AgentExecution).where(
                    AgentExecution.execution_id == execution_id
                )
            )

            if execution is None:
                raise LookupError(
                    f"Execution not found: {execution_id}"
                )

            if execution.status != "STARTED":
                raise ValueError(
                    f"Execution already finished: {execution_id}"
                )

            execution.status = status
            execution.completed_at = (
                AgentExecutionRepository._utc_now()
            )
            execution.process_time_ms = process_time_ms
            execution.error_message = error_message

            if execution_metadata is not None:
                existing_metadata = execution.execution_metadata or {}
                execution.execution_metadata = {
                    **existing_metadata,
                    **execution_metadata,
                }

            db.commit()
            db.refresh(execution)

            logger.info(
                "Agent execution finished | Agent: %s | "
                "Execution: %s | Status: %s | Duration: %s ms",
                execution.agent_code,
                execution.execution_id,
                status,
                process_time_ms,
            )

            return execution

        except Exception:
            db.rollback()

            logger.exception(
                "Failed to finish agent execution: %s",
                execution_id,
            )

            raise

    @staticmethod
    def get_by_execution_id(
        db: Session,
        execution_id: str,
    ) -> AgentExecution | None:

        return db.scalar(
            select(AgentExecution).where(
                AgentExecution.execution_id == execution_id
            )
        )

    @staticmethod
    def attach_project(
        db: Session,
        execution_id: str,
        project_id: str,
    ) -> None:

        try:
            execution = db.scalar(
                select(AgentExecution).where(
                    AgentExecution.execution_id == execution_id
                )
            )

            if execution is None:
                raise LookupError(
                    f"Execution not found: {execution_id}"
                )

            execution.project_id = project_id

            db.commit()

        except Exception:
            db.rollback()
            raise
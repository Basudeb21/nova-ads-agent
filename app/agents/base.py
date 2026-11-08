
from time import perf_counter_ns
from typing import Any

from app.database.models.agent import Agent
from app.database.connection import SessionLocal
from app.database.repositories.agent_execution_repository import (
    AgentExecutionRepository,
)
from app.core.logging import get_logger


class BaseAgent:

    def __init__(self, config: Agent):
        self.id = config.id
        self.agent_code = config.agent_code
        self.agent_name = config.agent_name
        self.display_name = config.display_name
        self.agent_type = config.agent_type
        self.role = config.role
        self.description = config.description
        self.technology = config.technology
        self.responsibilities: Any = config.responsibilities
        self.execution_order = config.execution_order
        self.is_active = config.is_active

        self.logger = get_logger(
            f"nova.agent.{self.agent_code}"
        )

    def initialize(self) -> None:
        """
        Common initialization controller.

        Automatically records initialization success or failure.
        Individual agents implement their initialization in _initialize().
        """

        db = SessionLocal()
        execution = None
        process_start = perf_counter_ns()

        try:
            execution = AgentExecutionRepository.create_execution(
                db=db,
                agent_code=self.agent_code,
                execution_type="INITIALIZATION",
                project_id=None,
                execution_metadata={
                    "agent_name": self.agent_name,
                    "agent_type": self.agent_type,
                    "role": self.role,
                },
            )

            self.logger.info(
                "Initializing agent: %s",
                self.agent_name,
            )

            self._initialize()

            process_time_ms = (
                perf_counter_ns() - process_start
            ) // 1_000_000

            AgentExecutionRepository.finish_execution(
                db=db,
                execution_id=execution.execution_id,
                status="SUCCESS",
                process_time_ms=process_time_ms,
            )

            self.logger.info(
                "%s initialized successfully.",
                self.agent_name,
            )

        except Exception as exc:

            if execution is not None:
                process_time_ms = (
                    perf_counter_ns() - process_start
                ) // 1_000_000

                try:
                    AgentExecutionRepository.finish_execution(
                        db=db,
                        execution_id=execution.execution_id,
                        status="FAILED",
                        process_time_ms=process_time_ms,
                        error_message=str(exc),
                    )

                except Exception:
                    self.logger.exception(
                        "Could not record initialization failure "
                        "for agent %s.",
                        self.agent_code,
                    )

            self.logger.exception(
                "Agent initialization failed: %s",
                self.agent_name,
            )

            raise

        finally:
            db.close()

    def _initialize(self) -> None:
        """
        Agent-specific initialization.

        Override this method in individual agent classes.
        """
        pass

    def get_identity(self) -> dict:
        return {
            "id": self.id,
            "agent_code": self.agent_code,
            "agent_name": self.agent_name,
            "display_name": self.display_name,
            "agent_type": self.agent_type,
            "role": self.role,
            "technology": self.technology,
            "responsibilities": self.responsibilities,
            "execution_order": self.execution_order,
            "is_active": self.is_active,
        }

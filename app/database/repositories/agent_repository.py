from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.agent import Agent
from app.core.logging import get_logger


logger = get_logger("nova.repository.agent")


class AgentRepository:

    @staticmethod
    def get_by_code(
        db: Session,
        agent_code: str,
    ) -> Agent | None:

        statement = select(Agent).where(
            Agent.agent_code == agent_code,
            Agent.is_active.is_(True),
        )

        agent = db.scalar(statement)

        if agent:
            logger.info(
                "Agent loaded: %s",
                agent.agent_code,
            )
        else:
            logger.warning(
                "Active agent not found: %s",
                agent_code,
            )

        return agent
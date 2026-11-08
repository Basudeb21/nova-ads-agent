
from app.agents.base import BaseAgent


class RequirementsAnalysisAgent(BaseAgent):

    def _initialize(self) -> None:

        if not self.is_active:
            raise RuntimeError(
                f"Agent {self.agent_code} is inactive."
            )

        if self.agent_type != "requirements_analyst":
            raise RuntimeError(
                f"Agent {self.agent_code} is not a Requirements Analyst."
            )

        self.logger.info(
            "%s is initializing as Requirements Analysis Agent.",
            self.agent_name,
        )

        print()
        print("=" * 55)
        print(f"  {self.display_name}")
        print("=" * 55)
        print(f"  Agent Code : {self.agent_code}")
        print(f"  Role       : {self.role}")
        print(f"  Technology : {self.technology}")
        print("=" * 55)
        print("  Status: INITIALIZED")
        print("=" * 55)
        print()

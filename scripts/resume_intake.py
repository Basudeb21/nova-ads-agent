
import asyncio

from app.intake.coordinator import IntakeCoordinator

SESSION_ID = "6aebdaf5-c962-4222-b1de-b8e94fe108a9"


async def main():
    coordinator = IntakeCoordinator(
        loop=asyncio.get_running_loop()
    )

    coordinator.initialize()

    await coordinator.resume_intake(SESSION_ID)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nIntake stopped.")

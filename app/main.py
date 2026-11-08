import asyncio

from app.core.logging import setup_logging, get_logger
from app.intake.coordinator import IntakeCoordinator
from app.services.storage.input_watcher import InputWatcher


setup_logging()

logger = get_logger("nova.main")


async def start_application():

    logger.info("NOVA ADS STUDIO starting...")

    coordinator = IntakeCoordinator(
        loop=asyncio.get_running_loop(),
    )

    watcher = None

    try:
        coordinator.initialize()

        watcher = InputWatcher(
            on_image_ready=coordinator.on_product_image,
        )

        watcher.start()

        logger.info("NOVA ADS STUDIO is ready.")

        print("\nNOVA ADS STUDIO IS RUNNING")
        print("Upload a product image into storage/input/")
        print("Press CTRL+C to stop.\n")

        await asyncio.Event().wait()

    finally:
        if watcher is not None:
            watcher.stop()

        logger.info("NOVA ADS STUDIO stopped.")


if __name__ == "__main__":

    try:
        asyncio.run(start_application())

    except KeyboardInterrupt:
        print("\nNOVA ADS STUDIO shutting down...")
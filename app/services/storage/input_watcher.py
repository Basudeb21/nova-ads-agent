import threading
import time

from pathlib import Path
from collections.abc import Callable

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from app.core.config import INPUT_DIR
from app.core.logging import get_logger


logger = get_logger("nova.storage.watcher")

SUPPORTED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".tif",
    ".tiff",
}


class ProductImageHandler(FileSystemEventHandler):

    def __init__(
        self,
        on_image_ready: Callable[[Path], None] | None = None,
        stable_checks: int = 3,
        check_interval: float = 1.0,
        timeout: int = 120,
    ):
        super().__init__()

        self.on_image_ready = on_image_ready
        self.stable_checks = stable_checks
        self.check_interval = check_interval
        self.timeout = timeout

        self.lock = threading.Lock()
        self.pending_files: set[str] = set()
        self.completed_files: set[str] = set()

    def on_created(self, event):
        if not event.is_directory:
            self._schedule_file(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._schedule_file(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._schedule_file(event.dest_path)

    def on_deleted(self, event):
        if event.is_directory:
            return

        file_key = str(Path(event.src_path).resolve())

        with self.lock:
            self.pending_files.discard(file_key)
            self.completed_files.discard(file_key)

    def _schedule_file(self, file_path: str):

        path = Path(file_path)

        if path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
            return

        file_key = str(path.resolve())

        with self.lock:
            if file_key in self.pending_files:
                return

            if file_key in self.completed_files:
                return

            self.pending_files.add(file_key)

        logger.info("New image detected: %s", path.name)

        worker = threading.Thread(
            target=self._wait_for_completion,
            args=(path, file_key),
            daemon=True,
        )
        worker.start()

    def _wait_for_completion(self, path: Path, file_key: str):

        stable_count = 0
        previous_state = None
        start_time = time.monotonic()

        try:
            while time.monotonic() - start_time < self.timeout:

                if not path.is_file():
                    stable_count = 0
                    previous_state = None
                    time.sleep(self.check_interval)
                    continue

                stat = path.stat()

                current_state = (
                    stat.st_size,
                    stat.st_mtime_ns,
                )

                if stat.st_size == 0:
                    stable_count = 0
                elif current_state == previous_state:
                    stable_count += 1
                else:
                    stable_count = 1

                previous_state = current_state

                if stable_count >= self.stable_checks:

                    with self.lock:
                        self.pending_files.discard(file_key)
                        self.completed_files.add(file_key)

                    logger.info(
                        "Image upload completed: %s | Size: %s bytes",
                        path.name,
                        stat.st_size,
                    )

                    print(f"\n[IMAGE READY] {path.name}")

                    if self.on_image_ready is not None:
                        self.on_image_ready(path)

                    return

                time.sleep(self.check_interval)

            logger.warning("Image upload timed out: %s", path.name)

        except FileNotFoundError:
            logger.warning("Image disappeared during upload: %s", path.name)

        except Exception:
            logger.exception("Error checking image upload: %s", path.name)

        finally:
            with self.lock:
                self.pending_files.discard(file_key)


class InputWatcher:

    def __init__(
        self,
        on_image_ready: Callable[[Path], None] | None = None,
    ):
        self.input_dir = INPUT_DIR

        self.handler = ProductImageHandler(
            on_image_ready=on_image_ready,
        )

        self.observer = Observer()

    def start(self):

        self.input_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.observer.schedule(
            self.handler,
            str(self.input_dir),
            recursive=False,
        )

        self.observer.start()

        logger.info("Input watcher started: %s", self.input_dir)

        print("\n" + "=" * 55)
        print("       NILADITTYA - INPUT MONITORING")
        print("=" * 55)
        print(f"Watching: {self.input_dir}")
        print("Status  : RUNNING")
        print("Waiting for product images...")
        print("=" * 55)

    def stop(self):

        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()

        logger.info("Input watcher stopped.")
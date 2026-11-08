import json
import shutil

from pathlib import Path
from typing import Any

from app.core.config import ROOT_DIR, STORAGE_DIR


class FileStorage:

    @staticmethod
    def relative_path(path: Path) -> str:
        return path.relative_to(ROOT_DIR).as_posix()

    @staticmethod
    def prepare_project_directories(
        project_id: str,
    ) -> dict[str, Path]:

        project_root = STORAGE_DIR / project_id

        paths = {
            "root": project_root,
            "product_images": (
                project_root / "input" / "product_imgs"
            ),
            "assets": project_root / "asset",
            "requirements": STORAGE_DIR / "re",
        }

        for path in paths.values():
            path.mkdir(parents=True, exist_ok=True)

        return paths

    @staticmethod
    def move_product_image(
        source: str | Path,
        destination_directory: Path,
    ) -> Path:

        source_path = Path(source).resolve()

        if not source_path.is_file():
            raise FileNotFoundError(
                f"Product image not found: {source_path}"
            )

        destination = destination_directory / source_path.name

        if destination.exists():
            raise FileExistsError(
                f"Product image already exists: {destination}"
            )

        shutil.move(
            str(source_path),
            str(destination),
        )

        return destination

    @staticmethod
    def move_brand_logo(
        source: str | Path,
        destination_directory: Path,
    ) -> Path:

        source_path = Path(source).resolve()

        if not source_path.is_file():
            raise FileNotFoundError(
                f"Brand logo not found: {source_path}"
            )

        destination = (
            destination_directory
            / f"brand_logo{source_path.suffix.lower()}"
        )

        shutil.move(
            str(source_path),
            str(destination),
        )

        return destination

    @staticmethod
    def write_requirements(
        project_id: str,
        requirements: dict[str, Any],
    ) -> Path:

        requirements_directory = STORAGE_DIR / "re"
        requirements_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination = (
            requirements_directory / f"{project_id}.txt"
        )

        with destination.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                requirements,
                file,
                indent=4,
                ensure_ascii=False,
            )

        return destination

    @staticmethod
    def restore_file(
        current_path: Path,
        original_path: Path,
    ) -> None:

        if current_path.exists():
            original_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            shutil.move(
                str(current_path),
                str(original_path),
            )

    @staticmethod
    def remove_project_directory(
        project_id: str,
    ) -> None:

        project_directory = STORAGE_DIR / project_id

        if project_directory.exists():
            shutil.rmtree(project_directory)
import uuid

from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter_ns

from sqlalchemy.orm import Session

from app.agents.base import BaseAgent
from app.database.connection import SessionLocal
from app.database.repositories.agent_execution_repository import (
    AgentExecutionRepository,
)
from app.database.repositories.project_repository import (
    ProjectRepository,
    ProjectRequirementsRepository,
)
from app.services.storage.file_storage import FileStorage
from app.schemas.requirements.intake import IntakeSessionState


class WorkflowOrchestrator(BaseAgent):

    def _initialize(self) -> None:

        if not self.is_active:
            raise RuntimeError(
                f"Agent {self.agent_code} is inactive."
            )

        if self.agent_type != "orchestrator":
            raise RuntimeError(
                f"Agent {self.agent_code} is not an orchestrator."
            )

        self.logger.info(
            "%s is initializing as Workflow Orchestrator.",
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

    def create_project(
        self,
        intake_state: IntakeSessionState,
    ) -> dict:

        db = SessionLocal()

        execution = None
        project_id = str(uuid.uuid4())

        process_start = perf_counter_ns()

        moved_files: list[tuple[Path, Path]] = []
        project_created = False

        project_paths = None

        try:
            requirements = intake_state.requirements

            if intake_state.status != "CONFIRMED":
                raise ValueError(
                    "Intake session has not been confirmed."
                )

            if not requirements.validation.confirmed_by_user:
                raise ValueError(
                    "Requirements have not been confirmed by the user."
                )

            if not requirements.validation.is_complete:
                raise ValueError(
                    "Requirements are incomplete."
                )

            if not requirements.project.project_name:
                raise ValueError(
                    "Project name is missing."
                )

            product_asset = next(
                (
                    asset
                    for asset in intake_state.assets
                    if asset.asset_type == "product_image"
                    and asset.upload_status == "ready"
                ),
                None,
            )

            if product_asset is None or not product_asset.file_path:
                raise ValueError(
                    "A ready product image is required."
                )

            product_source = Path(product_asset.file_path).resolve()

            if not product_source.is_file():
                raise FileNotFoundError(
                    f"Product image does not exist: {product_source}"
                )

            execution = AgentExecutionRepository.create_execution(
                db=db,
                agent_code=self.agent_code,
                execution_type="PROJECT_CREATION",
                execution_metadata={
                    "intake_session_id": str(intake_state.session_id),
                    "project_name": requirements.project.project_name,
                },
            )

            project_paths = FileStorage.prepare_project_directories(
                project_id
            )

            product_size = product_source.stat().st_size
            product_format = product_source.suffix.lstrip(".").upper()

            product_destination = FileStorage.move_product_image(
                product_source,
                project_paths["product_images"],
            )

            moved_files.append(
                (product_destination, product_source)
            )

            product_relative_path = FileStorage.relative_path(
                product_destination
            )

            # Optional brand logo.
            logo_asset = next(
                (
                    asset
                    for asset in intake_state.assets
                    if asset.asset_type == "brand_logo"
                    and asset.upload_status == "ready"
                    and asset.file_path
                ),
                None,
            )

            if requirements.brand.logo_required and logo_asset is None:
                raise ValueError(
                    "A brand logo is required but was not uploaded."
                )

            if logo_asset is not None:
                logo_source = Path(logo_asset.file_path).resolve()

                logo_destination = FileStorage.move_brand_logo(
                    logo_source,
                    project_paths["assets"],
                )

                moved_files.append(
                    (logo_destination, logo_source)
                )

                requirements.brand.logo_path = (
                    FileStorage.relative_path(logo_destination)
                )

            requirements_json = requirements.model_dump(
                mode="json"
            )

            requirements_text_path = (
                FileStorage.write_requirements(
                    project_id,
                    requirements_json,
                )
            )

            project = ProjectRepository.create_project(
                db=db,
                project_data={
                    "project_id": project_id,
                    "project_name": requirements.project.project_name,
                    "original_filename": product_source.name,
                    "product_image_path": product_relative_path,
                    "image_format": product_format,
                    "image_size": product_size,
                    "status": "CREATED",
                },
            )

            project_created = True

            AgentExecutionRepository.attach_project(
                db=db,
                execution_id=execution.execution_id,
                project_id=project_id,
            )

            ProjectRequirementsRepository.create_requirements(
                db=db,
                requirements_data={
                    "project_id": project_id,
                    "schema_version": requirements.schema_version,
                    "requirements_json": requirements_json,
                    "requirements_text_path": (
                        FileStorage.relative_path(
                            requirements_text_path
                        )
                    ),
                    "confirmed_at": datetime.now(
                        timezone.utc
                    ).replace(tzinfo=None),
                },
            )

            process_time_ms = (
                perf_counter_ns() - process_start
            ) // 1_000_000

            AgentExecutionRepository.finish_execution(
                db=db,
                execution_id=execution.execution_id,
                status="SUCCESS",
                process_time_ms=process_time_ms,
                execution_metadata={
                    "project_id": project_id,
                },
            )

            self.logger.info(
                "Project created successfully | Project ID: %s",
                project_id,
            )

            return {
                "success": True,
                "project_id": project.project_id,
                "project_name": project.project_name,
                "product_image_path": project.product_image_path,
                "requirements_path": FileStorage.relative_path(
                    requirements_text_path
                ),
                "status": project.status,
            }

        except Exception as exc:

            self.logger.exception(
                "Project creation failed."
            )

            # Restore uploaded files if project creation fails.
            for current_path, original_path in reversed(moved_files):
                try:
                    FileStorage.restore_file(
                        current_path,
                        original_path,
                    )
                except Exception:
                    self.logger.exception(
                        "Could not restore file: %s",
                        original_path,
                    )

            if project_created:
                try:
                    ProjectRepository.delete_project(
                        db,
                        project_id,
                    )
                except Exception:
                    self.logger.exception(
                        "Could not roll back project: %s",
                        project_id,
                    )

            if project_paths is not None:
                FileStorage.remove_project_directory(
                    project_id
                )

            requirements_file = (
                FileStorage.relative_path(
                    FileStorage.ROOT_DIR / "storage" / "re" / f"{project_id}.txt"
                )
                if False else None
            )

            if execution is not None:
                try:
                    process_time_ms = (
                        perf_counter_ns() - process_start
                    ) // 1_000_000

                    AgentExecutionRepository.finish_execution(
                        db=db,
                        execution_id=execution.execution_id,
                        status="FAILED",
                        process_time_ms=process_time_ms,
                        error_message=str(exc),
                    )

                except Exception:
                    self.logger.exception(
                        "Could not record project creation failure."
                    )

            raise

        finally:
            db.close()
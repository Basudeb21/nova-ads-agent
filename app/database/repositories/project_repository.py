from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.database.models.project import (
    Project,
    ProjectRequirementRecord,
)


class ProjectRepository:

    @staticmethod
    def create_project(
        db: Session,
        project_data: dict,
    ) -> Project:

        try:
            project = Project(**project_data)

            db.add(project)
            db.commit()
            db.refresh(project)

            return project

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def get_by_project_id(
        db: Session,
        project_id: str,
    ) -> Project | None:

        return db.scalar(
            select(Project).where(
                Project.project_id == project_id
            )
        )

    @staticmethod
    def delete_project(
        db: Session,
        project_id: str,
    ) -> None:

        try:
            db.execute(
                delete(Project).where(
                    Project.project_id == project_id
                )
            )
            db.commit()

        except Exception:
            db.rollback()
            raise


class ProjectRequirementsRepository:

    @staticmethod
    def create_requirements(
        db: Session,
        requirements_data: dict,
    ) -> ProjectRequirementRecord:

        try:
            record = ProjectRequirementRecord(
                **requirements_data
            )

            db.add(record)
            db.commit()
            db.refresh(record)

            return record

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def get_by_project_id(
        db: Session,
        project_id: str,
    ) -> ProjectRequirementRecord | None:

        return db.scalar(
            select(ProjectRequirementRecord).where(
                ProjectRequirementRecord.project_id == project_id
            )
        )

import asyncio
from pathlib import Path

from app.core.config import INPUT_DIR
from app.core.logging import get_logger
from app.database.connection import SessionLocal
from app.database.models.agent import Agent

from app.agents.orchestrators.workflow_orchestrator.agent import (
    WorkflowOrchestrator,
)
from app.agents.requirements_analysis.agent import RequirementsAnalysisAgent
from app.agents.requirements_analysis.conversation_service import (
    RiyaConversationService,
)
from app.agents.requirements_analysis.review import RequirementsReviewService

from app.intake.modules.register import register_builtin_modules

from app.schemas.requirements.intake import (
    IntakeSessionState,
    IntakeAsset,
)

from app.services.storage.intake_session_repository import (
    IntakeSessionRepository,
)

logger = get_logger("nova.intake.coordinator")


class IntakeCoordinator:

    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop
        self.intake_lock = asyncio.Lock()
        self.orchestrator = None
        self.riya = None
        self.riya_initialized = False

    def initialize(self) -> None:
        register_builtin_modules()

        db = SessionLocal()

        try:
            nil_config = db.query(Agent).filter(
                Agent.agent_code == "1001"
            ).one_or_none()

            riya_config = db.query(Agent).filter(
                Agent.agent_code == "1010"
            ).one_or_none()

            if nil_config is None:
                raise RuntimeError("Niladittya (1001) not found.")

            if riya_config is None:
                raise RuntimeError("Riya (1010) not found.")

            self.orchestrator = WorkflowOrchestrator(nil_config)
            self.riya = RequirementsAnalysisAgent(riya_config)

        finally:
            db.close()

        self.orchestrator.initialize()
        logger.info("Intake coordinator initialized.")

    def on_product_image(self, image_path: Path) -> None:
        future = asyncio.run_coroutine_threadsafe(
            self._start_intake(image_path),
            self.loop,
        )

        future.add_done_callback(self._handle_future_result)

    @staticmethod
    def _handle_future_result(future) -> None:
        try:
            future.result()
        except Exception:
            logger.exception("Product intake workflow failed.")

    async def _initialize_riya(self) -> None:
        if not self.riya_initialized:
            self.riya.initialize()
            self.riya_initialized = True

    async def _start_intake(self, image_path: Path) -> None:
        async with self.intake_lock:

            if not image_path.is_file():
                logger.warning(
                    "Uploaded image no longer exists: %s",
                    image_path,
                )
                return

            if self.orchestrator is None or self.riya is None:
                raise RuntimeError(
                    "Intake coordinator is not initialized."
                )

            await self._initialize_riya()

            state = IntakeSessionState(
                content_type="advertising",
                module_version="1.0",
                assets=[
                    IntakeAsset(
                        asset_type="product_image",
                        original_filename=image_path.name,
                        file_path=str(image_path.resolve()),
                        upload_status="ready",
                    )
                ],
            )

            if not IntakeSessionRepository.create_session(state):
                raise RuntimeError(
                    f"Could not create intake session: {state.session_id}"
                )

            await self._run_conversation(
                str(state.session_id),
                image_path.name,
            )

    async def resume_intake(self, session_id: str) -> None:
        async with self.intake_lock:

            state = IntakeSessionRepository.get_session(
                session_id,
                refresh_ttl=False,
            )

            if state is None:
                raise KeyError(
                    f"Intake session not found: {session_id}"
                )

            if state.status != "COLLECTING":
                raise RuntimeError(
                    f"Cannot resume session with status: {state.status}"
                )

            if self.orchestrator is None or self.riya is None:
                raise RuntimeError(
                    "Intake coordinator is not initialized."
                )

            await self._initialize_riya()

            product_name = next(
                (
                    asset.original_filename
                    for asset in state.assets
                    if asset.asset_type == "product_image"
                ),
                "Previously uploaded product",
            )

            print(f"\nResuming session: {session_id}")
            print(f"Product: {product_name}")

            await self._run_conversation(
                session_id,
                product_name,
            )

    async def _run_conversation(
        self,
        session_id: str,
        product_name: str,
    ) -> None:

        conversation = RiyaConversationService()

        print("\n" + "=" * 60)
        print("RIYA - REQUIREMENTS ANALYSIS")
        print("=" * 60)
        print(f"Product : {product_name}")
        print(f"Session : {session_id}")
        print("=" * 60)

        turn = await conversation.get_next_turn(session_id)

        while turn is not None:

            print(f"\nRIYA: {turn.message}")

            answer = await asyncio.to_thread(
                input,
                "\nYOU: ",
            )

            if not answer.strip():
                print("Please enter an answer.")
                continue

            turn = await conversation.submit_answer(
                session_id,
                answer,
            )

        await self._collect_required_logo(session_id)

        await self._review_and_confirm(
            session_id,
            conversation,
        )

    async def _collect_required_logo(
        self,
        session_id: str,
    ) -> None:

        state = IntakeSessionRepository.get_session(
            session_id,
            refresh_ttl=False,
        )

        if state is None:
            raise KeyError(
                f"Intake session not found: {session_id}"
            )

        if not state.requirements.brand.logo_required:
            return

        # Check whether a logo is already registered.
        existing_logo = next(
            (
                asset
                for asset in state.assets
                if asset.asset_type == "brand_logo"
                and asset.upload_status == "ready"
                and asset.file_path
                and Path(asset.file_path).is_file()
            ),
            None,
        )

        if existing_logo:
            if not state.requirements.brand.logo_path:
                def update_logo_path(current_state):
                    current_state.requirements.brand.logo_path = (
                        existing_logo.file_path
                    )

                IntakeSessionRepository.update_session(
                    session_id,
                    update_logo_path,
                )
            return

        print("\n" + "=" * 60)
        print("BRAND LOGO UPLOAD REQUIRED")
        print("=" * 60)
        print(f"Place your logo image inside: {INPUT_DIR}")
        print("Supported formats: PNG, JPG, JPEG, WEBP")

        while True:

            filename = await asyncio.to_thread(
                input,
                "\nEnter logo filename: ",
            )

            filename = filename.strip().strip('"')

            if not filename:
                print("Please enter a filename.")
                continue

            logo_path = (INPUT_DIR / filename).resolve()

            if logo_path.parent != INPUT_DIR.resolve():
                print("Please enter a filename inside the input folder.")
                continue

            if not logo_path.is_file():
                print("Logo file not found. Upload it and try again.")
                continue

            if logo_path.suffix.lower() not in {
                ".png",
                ".jpg",
                ".jpeg",
                ".webp",
            }:
                print("Unsupported logo format.")
                continue

            break

        def register_logo(current_state):
            # Avoid duplicate asset registration.
            current_state.assets = [
                asset
                for asset in current_state.assets
                if not (
                    asset.asset_type == "brand_logo"
                    and asset.original_filename == logo_path.name
                )
            ]

            current_state.assets.append(
                IntakeAsset(
                    asset_type="brand_logo",
                    original_filename=logo_path.name,
                    file_path=str(logo_path),
                    upload_status="ready",
                )
            )

            current_state.requirements.brand.logo_path = str(
                logo_path
            )

        updated = IntakeSessionRepository.update_session(
            session_id,
            register_logo,
        )

        if updated is None:
            raise RuntimeError("Could not register brand logo.")

        print(f"\n[BRAND LOGO READY] {logo_path.name}")

    async def _review_and_confirm(
        self,
        session_id: str,
        conversation: RiyaConversationService,
    ) -> None:

        state = conversation.question_service.get_session(
            session_id
        )

        if state is None:
            raise KeyError(
                f"Intake session not found: {session_id}"
            )

        validation = RequirementsReviewService.validate(state)

        if not validation["is_complete"]:
            print("\nRequirements are incomplete.")
            print(
                "Missing:",
                ", ".join(validation["missing_fields"]),
            )
            return

        print("\n" + "=" * 60)
        print(RequirementsReviewService.generate_summary(state))
        print("=" * 60)

        answer = await asyncio.to_thread(
            input,
            "\nConfirm project creation? [yes/no]: ",
        )

        if answer.strip().lower() not in {"yes", "y"}:
            print("\nProject creation not confirmed.")
            print(f"Session remains available: {session_id}")
            return

        final_state = RequirementsReviewService.confirm(
            session_id,
            orchestrator=self.orchestrator,
        )

        print("\n" + "=" * 60)
        print("PROJECT CREATED SUCCESSFULLY")
        print("=" * 60)

        for message in final_state.messages[-2:]:
            print(message.content)

        print("=" * 60)

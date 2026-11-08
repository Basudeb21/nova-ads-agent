
from app.intake.engine.catalog_registry import (
    intake_catalog_registry,
)

from app.intake.modules.advertising.module import (
    ADVERTISING_MODULE,
)


def register_builtin_modules() -> None:

    if not intake_catalog_registry.is_registered(
        ADVERTISING_MODULE.content_type,
        ADVERTISING_MODULE.version,
    ):

        intake_catalog_registry.register(
            ADVERTISING_MODULE,
            make_active=True,
        )


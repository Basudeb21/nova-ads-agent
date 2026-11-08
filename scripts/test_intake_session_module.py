
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.schemas.requirements.intake import IntakeSessionState

from app.services.storage.intake_session_repository import (
    IntakeSessionRepository,
)


def main():

    print("=" * 60)
    print("NOVA - MODULE-AWARE INTAKE SESSION TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. ADVERTISING SESSION
    # --------------------------------------------------------

    advertising_session = IntakeSessionState(
        content_type="advertising",
        module_version="1.0",
    )

    assert advertising_session.content_type == "advertising"
    assert advertising_session.module_version == "1.0"

    print("1. Advertising session creation: SUCCESS")

    # --------------------------------------------------------
    # 2. HIRING SESSION
    # --------------------------------------------------------

    hiring_session = IntakeSessionState(
        content_type="hiring",
        module_version="2.0",
    )

    assert hiring_session.content_type == "hiring"
    assert hiring_session.module_version == "2.0"

    print("2. Hiring session creation: SUCCESS")

    # --------------------------------------------------------
    # 3. REDIS PERSISTENCE
    # --------------------------------------------------------

    assert IntakeSessionRepository.create_session(
        advertising_session
    )

    assert IntakeSessionRepository.create_session(
        hiring_session
    )

    print("3. Module-aware Redis persistence: SUCCESS")

    # --------------------------------------------------------
    # 4. RETRIEVAL
    # --------------------------------------------------------

    loaded_advertising = IntakeSessionRepository.get_session(
        advertising_session.session_id
    )

    loaded_hiring = IntakeSessionRepository.get_session(
        hiring_session.session_id
    )

    assert loaded_advertising is not None
    assert loaded_hiring is not None

    assert loaded_advertising.content_type == "advertising"
    assert loaded_advertising.module_version == "1.0"

    assert loaded_hiring.content_type == "hiring"
    assert loaded_hiring.module_version == "2.0"

    print("4. Module identity retrieval: SUCCESS")

    # --------------------------------------------------------
    # 5. PROTECT MODULE IDENTITY
    # --------------------------------------------------------

    def change_module(session):
        session.content_type = "hiring"
        session.module_version = "2.0"

    try:

        IntakeSessionRepository.update_session(
            advertising_session.session_id,
            change_module,
        )

        raise AssertionError(
            "Active session module identity was changed."
        )

    except ValueError:
        print("5. Module identity protection: SUCCESS")

    # --------------------------------------------------------
    # 6. VERIFY ORIGINAL MODULE
    # --------------------------------------------------------

    unchanged = IntakeSessionRepository.get_session(
        advertising_session.session_id
    )

    assert unchanged is not None
    assert unchanged.content_type == "advertising"
    assert unchanged.module_version == "1.0"

    print("6. Original module preservation: SUCCESS")

    # --------------------------------------------------------
    # 7. CLEANUP
    # --------------------------------------------------------

    IntakeSessionRepository.delete_session(
        advertising_session.session_id
    )

    IntakeSessionRepository.delete_session(
        hiring_session.session_id
    )

    print("7. Test session cleanup: SUCCESS")

    print("=" * 60)
    print("MODULE-AWARE SESSION TEST SUCCESSFUL")
    print("=" * 60)


if __name__ == "__main__":
    main()

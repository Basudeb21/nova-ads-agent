
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.schemas.requirements.intake import (
    IntakeSessionState,
    IntakeMessage,
)

from app.services.storage.intake_session_repository import (
    IntakeSessionRepository,
)


def main():

    print("=" * 60)
    print("NOVA ADS STUDIO - ATOMIC INTAKE SESSION TEST")
    print("=" * 60)

    state = IntakeSessionState()

    # --------------------------------------------------------
    # 1. CREATE
    # --------------------------------------------------------

    created = IntakeSessionRepository.create_session(state)

    assert created is True

    print("1. Session creation: SUCCESS")

    # --------------------------------------------------------
    # 2. PREVENT DUPLICATE CREATION
    # --------------------------------------------------------

    duplicate = IntakeSessionRepository.create_session(state)

    assert duplicate is False

    print("2. Duplicate creation prevention: SUCCESS")

    # --------------------------------------------------------
    # 3. RETRIEVE
    # --------------------------------------------------------

    loaded = IntakeSessionRepository.get_session(
        state.session_id
    )

    assert loaded is not None
    assert loaded.session_id == state.session_id

    print("3. Session retrieval: SUCCESS")

    # --------------------------------------------------------
    # 4. ATOMIC UPDATE
    # --------------------------------------------------------

    def add_first_message(session):

        session.messages.append(
            IntakeMessage(
                role="user",
                content="Create an Instagram advertisement.",
            )
        )

    updated = IntakeSessionRepository.update_session(
        state.session_id,
        add_first_message,
    )

    assert updated is not None
    assert len(updated.messages) == 1

    print("4. Atomic session update: SUCCESS")

    # --------------------------------------------------------
    # 5. CONCURRENT UPDATES
    # --------------------------------------------------------

    def add_message(content):

        def updater(session):

            session.messages.append(
                IntakeMessage(
                    role="user",
                    content=content,
                )
            )

        result = IntakeSessionRepository.update_session(
            state.session_id,
            updater,
        )

        assert result is not None

    messages = [
        "My target platform is Instagram.",
        "I prefer a premium visual style.",
    ]

    with ThreadPoolExecutor(max_workers=2) as executor:

        futures = [
            executor.submit(add_message, message)
            for message in messages
        ]

        for future in futures:
            future.result()

    final_state = IntakeSessionRepository.get_session(
        state.session_id
    )

    assert final_state is not None
    assert len(final_state.messages) == 3

    final_contents = {
        message.content
        for message in final_state.messages
    }

    assert "Create an Instagram advertisement." in final_contents
    assert "My target platform is Instagram." in final_contents
    assert "I prefer a premium visual style." in final_contents

    print("5. Concurrent updates: SUCCESS")
    print("   No session messages were lost.")

    # --------------------------------------------------------
    # 6. TTL
    # --------------------------------------------------------

    ttl = IntakeSessionRepository.get_session_ttl(
        state.session_id
    )

    assert ttl > 0

    print(f"6. Session expiration: SUCCESS ({ttl} seconds)")

    # --------------------------------------------------------
    # 7. DELETE
    # --------------------------------------------------------

    deleted = IntakeSessionRepository.delete_session(
        state.session_id
    )

    assert deleted is True

    assert not IntakeSessionRepository.session_exists(
        state.session_id
    )

    print("7. Session deletion: SUCCESS")

    # --------------------------------------------------------
    # 8. MISSING SESSION
    # --------------------------------------------------------

    missing = IntakeSessionRepository.get_session(
        state.session_id
    )

    assert missing is None

    print("8. Missing session handling: SUCCESS")

    print("=" * 60)
    print("ATOMIC INTAKE SESSION TEST SUCCESSFUL")
    print("=" * 60)


if __name__ == "__main__":
    main()

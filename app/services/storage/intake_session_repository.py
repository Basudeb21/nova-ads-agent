
from collections.abc import Callable
from uuid import UUID

import redis
from redis.exceptions import WatchError

from app.core.config import INTAKE_SESSION_TTL_SECONDS
from app.core.logging import get_logger
from app.core.redis_connection import redis_client
from app.schemas.requirements.intake import IntakeSessionState


logger = get_logger("nova.intake.session")


class IntakeSessionRepository:

    KEY_PREFIX = "nova:intake:session:"

    @classmethod
    def _get_key(cls, session_id: UUID | str) -> str:
        return f"{cls.KEY_PREFIX}{session_id}"

    # ========================================================
    # CREATE SESSION
    # ========================================================

    @classmethod
    def create_session(
        cls,
        state: IntakeSessionState,
    ) -> bool:
        """
        Create a new session without overwriting an existing one.
        """

        key = cls._get_key(state.session_id)

        try:
            result = redis_client.set(
                key,
                state.model_dump_json(),
                ex=INTAKE_SESSION_TTL_SECONDS,
                nx=True,
            )

            if result:
                logger.info(
                    "Intake session created: %s",
                    state.session_id,
                )
                return True

            logger.warning(
                "Intake session already exists: %s",
                state.session_id,
            )
            return False

        except redis.RedisError:
            logger.exception(
                "Failed to create intake session: %s",
                state.session_id,
            )
            raise

    # ========================================================
    # GET SESSION
    # ========================================================

    @classmethod
    def get_session(
        cls,
        session_id: UUID | str,
        refresh_ttl: bool = True,
    ) -> IntakeSessionState | None:

        key = cls._get_key(session_id)

        try:
            session_json = redis_client.get(key)

            if session_json is None:
                return None

            state = IntakeSessionState.model_validate_json(
                session_json
            )

            if refresh_ttl:
                redis_client.expire(
                    key,
                    INTAKE_SESSION_TTL_SECONDS,
                )

            return state

        except redis.RedisError:
            logger.exception(
                "Failed to retrieve intake session: %s",
                session_id,
            )
            raise

    # ========================================================
    # ATOMIC SESSION UPDATE
    # ========================================================

    @classmethod
    def update_session(
        cls,
        session_id: UUID | str,
        updater: Callable[[IntakeSessionState], None],
        max_retries: int = 10,
    ) -> IntakeSessionState | None:
        """
        Atomically update a session using WATCH / MULTI / EXEC.

        The updater must only modify the supplied in-memory
        state. It must not perform external side effects.

        Returns:
            Updated IntakeSessionState.
            None if the session does not exist.

        Raises:
            RuntimeError if concurrent conflicts exceed retries.
            RedisError for Redis operation failures.
        """

        key = cls._get_key(session_id)

        for attempt in range(max_retries):

            try:
                with redis_client.pipeline() as pipe:

                    # Watch for concurrent changes.
                    pipe.watch(key)

                    session_json = pipe.get(key)

                    if session_json is None:
                        pipe.unwatch()

                        logger.warning(
                            "Cannot update missing session: %s",
                            session_id,
                        )
                        return None

                    state = IntakeSessionState.model_validate_json(
                        session_json
                    )
                    original_content_type = state.content_type
                    original_module_version = state.module_version

                    # Apply the requested in-memory changes.
                    updater(state)

                    if str(state.session_id) != str(session_id):
                        raise ValueError(
                            "Session ID cannot be changed during update."
                        )

                    if state.content_type != original_content_type:
                        raise ValueError(
                            "Content type cannot be changed during an active session."
                        )

                    if state.module_version != original_module_version:
                        raise ValueError(
                            "Module version cannot be changed during an active session."
                        )

                    # Start transaction.
                    pipe.multi()

                    # Save updated state and refresh TTL atomically.
                    pipe.set(
                        key,
                        state.model_dump_json(),
                        ex=INTAKE_SESSION_TTL_SECONDS,
                    )

                    pipe.execute()

                    logger.info(
                        "Intake session updated: %s",
                        session_id,
                    )

                    return state

            except WatchError:

                logger.warning(
                    "Session update conflict for %s. "
                    "Retry %s/%s",
                    session_id,
                    attempt + 1,
                    max_retries,
                )

                continue

            except redis.RedisError:
                logger.exception(
                    "Redis error updating session: %s",
                    session_id,
                )
                raise

        raise RuntimeError(
            f"Could not update session {session_id} "
            f"after {max_retries} concurrent retries."
        )

    # ========================================================
    # DELETE SESSION
    # ========================================================

    @classmethod
    def delete_session(
        cls,
        session_id: UUID | str,
    ) -> bool:

        key = cls._get_key(session_id)

        try:
            deleted = redis_client.delete(key)

            if deleted:
                logger.info(
                    "Intake session deleted: %s",
                    session_id,
                )

            return bool(deleted)

        except redis.RedisError:
            logger.exception(
                "Failed to delete intake session: %s",
                session_id,
            )
            raise

    # ========================================================
    # SESSION EXISTS
    # ========================================================

    @classmethod
    def session_exists(
        cls,
        session_id: UUID | str,
    ) -> bool:

        key = cls._get_key(session_id)

        try:
            return bool(redis_client.exists(key))

        except redis.RedisError:
            logger.exception(
                "Failed to check intake session: %s",
                session_id,
            )
            raise

    # ========================================================
    # SESSION TTL
    # ========================================================

    @classmethod
    def get_session_ttl(
        cls,
        session_id: UUID | str,
    ) -> int:

        key = cls._get_key(session_id)

        try:
            return redis_client.ttl(key)

        except redis.RedisError:
            logger.exception(
                "Failed to retrieve session TTL: %s",
                session_id,
            )
            raise

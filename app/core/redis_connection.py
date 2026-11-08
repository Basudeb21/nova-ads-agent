import redis

from app.core.config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB,
    REDIS_PASSWORD,
    REDIS_SOCKET_TIMEOUT,
    REDIS_CONNECT_TIMEOUT,
)

from app.core.logging import get_logger


logger = get_logger("nova.redis")


# ============================================================
# REDIS CLIENT
# ============================================================

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True,
    socket_timeout=REDIS_SOCKET_TIMEOUT,
    socket_connect_timeout=REDIS_CONNECT_TIMEOUT,
    health_check_interval=30,
)


# ============================================================
# CONNECTION TEST
# ============================================================

def test_redis_connection() -> bool:

    try:
        response = redis_client.ping()

        if response:
            logger.info(
                "Redis connection successful: %s:%s",
                REDIS_HOST,
                REDIS_PORT,
            )
            return True

        return False

    except redis.RedisError:
        logger.exception("Redis connection failed.")
        return False


# ============================================================
# CONNECTION CLOSE
# ============================================================

def close_redis_connection() -> None:

    try:
        redis_client.close()
        logger.info("Redis connection closed.")

    except redis.RedisError:
        logger.exception("Error closing Redis connection.")
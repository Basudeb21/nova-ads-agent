import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from app.core.redis_connection import (
    test_redis_connection,
)


def main():

    print("=" * 50)
    print("NOVA ADS STUDIO - REDIS CONNECTION TEST")
    print("=" * 50)

    if test_redis_connection():
        print("Redis connection: SUCCESS")
    else:
        print("Redis connection: FAILED")
        raise SystemExit(1)

    print("=" * 50)


if __name__ == "__main__":
    main()
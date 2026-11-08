from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import DATABASE_URL
from app.core.logging import get_logger


logger = get_logger("nova.database")


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
    connect_args={
        "init_command": "SET time_zone = '+00:00'"
    },
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db():
    db: Session = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def test_database_connection() -> bool:
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")

        logger.info("MySQL connection successful.")
        return True

    except Exception:
        logger.exception("MySQL connection failed.")
        return False
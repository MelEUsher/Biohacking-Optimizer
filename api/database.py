from __future__ import annotations

import os

import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()


class Base(DeclarativeBase):
    """Shared declarative base for all SQLAlchemy models."""


SessionLocal = sessionmaker(autocommit=False, autoflush=False)


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required.")
    return database_url


def get_engine(database_url: str | None = None):
    url = database_url or get_database_url()
    return sqlalchemy.create_engine(url, pool_pre_ping=True)


def get_session():
    engine = get_engine()
    return SessionLocal(bind=engine)


def check_database_connection(
    database_url: str | None = None,
) -> tuple[bool, str | None]:
    try:
        engine = get_engine(database_url=database_url)
        with engine.connect() as connection:
            connection.execute(sqlalchemy.text("SELECT 1"))
        return True, None
    except (SQLAlchemyError, ValueError) as exc:
        return False, str(exc)

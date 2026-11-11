import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


def create_database_engine() -> Engine:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        database_path = Path(__file__).resolve().parents[1] / "festa_ifc.db"
        database_url = f"sqlite:///{database_path.as_posix()}"

    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)


engine = create_database_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def initialize_database() -> None:
    from src import models  # noqa: F401

    Base.metadata.create_all(bind=engine)

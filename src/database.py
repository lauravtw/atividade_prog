import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

# Pega as configurações do secrets.toml (local ou nuvem)
config = st.secrets["database"]

url = (
    f"mysql+pymysql://{config['user']}:"
    f"{quote_plus(config['password'])}@"
    f"{config['host']}:{config['port']}/"
    f"{config['database']}"
)

# Cria o engine com suporte a reconexão automática
engine = create_engine(url, pool_pre_ping=True)

# Fábrica de sessões para o SQLAlchemy ORM
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

''' import os
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

    Base.metadata.create_all(bind=engine) '''

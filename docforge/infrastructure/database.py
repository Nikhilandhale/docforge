from __future__ import annotations

from sqlmodel import SQLModel, create_engine

from docforge.config import settings

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

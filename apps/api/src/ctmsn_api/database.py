from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from ctmsn_api.config import DATABASE_URL


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def migrate_db() -> None:
    migrations = [
        "ALTER TABLE workspaces ADD COLUMN name VARCHAR(255) NOT NULL DEFAULT ''",
        "ALTER TABLE workspaces ADD COLUMN context_json TEXT NOT NULL DEFAULT '{}'",
        "ALTER TABLE workspaces ADD COLUMN is_deleted DATETIME DEFAULT NULL",
    ]
    with engine.connect() as conn:
        for stmt in migrations:
            try:
                conn.execute(text(stmt))
                conn.commit()
            except Exception:
                conn.rollback()

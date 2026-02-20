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
    new_tables = [
        """CREATE TABLE IF NOT EXISTS formula_records (
            id VARCHAR(32) PRIMARY KEY,
            workspace_id VARCHAR(32) NOT NULL REFERENCES workspaces(id),
            name VARCHAR(255) NOT NULL,
            formula_json TEXT NOT NULL DEFAULT '{}',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS user_variables (
            id VARCHAR(32) PRIMARY KEY,
            workspace_id VARCHAR(32) NOT NULL REFERENCES workspaces(id),
            name VARCHAR(255) NOT NULL,
            type_tag VARCHAR(150),
            domain_type VARCHAR(50) NOT NULL,
            domain_json TEXT NOT NULL DEFAULT '{}',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS named_contexts (
            id VARCHAR(32) PRIMARY KEY,
            workspace_id VARCHAR(32) NOT NULL REFERENCES workspaces(id),
            name VARCHAR(255) NOT NULL,
            context_json TEXT NOT NULL DEFAULT '{}',
            is_active INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS network_snapshots (
            id VARCHAR(32) PRIMARY KEY,
            workspace_id VARCHAR(32) NOT NULL REFERENCES workspaces(id),
            network_json TEXT NOT NULL,
            context_json TEXT NOT NULL DEFAULT '{}',
            action VARCHAR(255) NOT NULL DEFAULT '',
            stack VARCHAR(10) NOT NULL DEFAULT 'undo',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS grades (
            id VARCHAR(32) PRIMARY KEY,
            workspace_id VARCHAR(32) NOT NULL UNIQUE REFERENCES workspaces(id),
            teacher_id VARCHAR(32) NOT NULL REFERENCES users(id),
            value INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )""",
    ]
    with engine.connect() as conn:
        for stmt in migrations:
            try:
                conn.execute(text(stmt))
                conn.commit()
            except Exception:
                conn.rollback()
        for stmt in new_tables:
            try:
                conn.execute(text(stmt))
                conn.commit()
            except Exception:
                conn.rollback()

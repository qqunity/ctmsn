from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import relationship

from ctmsn_api.database import Base


class Role(str, enum.Enum):
    student = "student"
    teacher = "teacher"


def _uuid_hex() -> str:
    return uuid.uuid4().hex


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String(32), primary_key=True, default=_uuid_hex)
    username = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(Role), nullable=False, default=Role.student)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    workspaces = relationship("Workspace", back_populates="owner")
    comments = relationship("Comment", back_populates="author")


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(String(32), primary_key=True, default=_uuid_hex)
    owner_id = Column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    scenario = Column(String(150), nullable=False)
    mode = Column(String(150), nullable=True)
    name = Column(String(255), nullable=False, default="")
    network_json = Column(Text, nullable=False, default="{}")
    context_json = Column(Text, nullable=False, default="{}")
    is_deleted = Column(DateTime(timezone=True), nullable=True, default=None)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    owner = relationship("User", back_populates="workspaces")
    comments = relationship("Comment", back_populates="workspace", order_by="Comment.created_at")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(String(32), primary_key=True, default=_uuid_hex)
    workspace_id = Column(String(32), ForeignKey("workspaces.id"), nullable=False, index=True)
    author_id = Column(String(32), ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    workspace = relationship("Workspace", back_populates="comments")
    author = relationship("User", back_populates="comments")

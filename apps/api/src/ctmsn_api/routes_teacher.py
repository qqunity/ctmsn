from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from ctmsn_api.auth import require_role
from ctmsn_api.database import get_db
from ctmsn_api.models import Comment, Role, User, Workspace

router = APIRouter(prefix="/api/teacher", tags=["teacher"])

_teacher_dep = require_role(Role.teacher)


class StudentInfo(BaseModel):
    id: str
    username: str
    workspace_count: int


class WorkspaceInfo(BaseModel):
    id: str
    name: str
    scenario: str
    mode: Optional[str]
    created_at: str
    updated_at: str


class CommentOut(BaseModel):
    id: str
    author_id: str
    author_username: str
    text: str
    created_at: str


class AddCommentReq(BaseModel):
    text: str


@router.get("/students", response_model=List[StudentInfo])
def list_students(
    teacher: User = Depends(_teacher_dep),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(User, func.count(Workspace.id))
        .outerjoin(Workspace, (Workspace.owner_id == User.id) & Workspace.is_deleted.is_(None))
        .filter(User.role == Role.student)
        .group_by(User.id)
        .all()
    )
    return [
        StudentInfo(id=u.id, username=u.username, workspace_count=cnt)
        for u, cnt in rows
    ]


@router.get("/students/{student_id}/workspaces", response_model=List[WorkspaceInfo])
def student_workspaces(
    student_id: str,
    teacher: User = Depends(_teacher_dep),
    db: Session = Depends(get_db),
):
    student = db.query(User).filter(User.id == student_id, User.role == Role.student).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    ws_list = (
        db.query(Workspace)
        .filter(Workspace.owner_id == student_id, Workspace.is_deleted.is_(None))
        .order_by(Workspace.created_at.desc())
        .all()
    )
    return [
        WorkspaceInfo(
            id=w.id, name=w.name, scenario=w.scenario, mode=w.mode,
            created_at=w.created_at.isoformat(), updated_at=w.updated_at.isoformat(),
        )
        for w in ws_list
    ]


@router.get("/workspaces/{workspace_id}")
def view_workspace(
    workspace_id: str,
    teacher: User = Depends(_teacher_dep),
    db: Session = Depends(get_db),
):
    from ctmsn_api.ops import get_variable_info, run_ops
    from ctmsn_api.registry import get as get_spec
    from ctmsn_api.serialize import serialize
    from ctmsn_api.sessions import context_from_json, network_from_json

    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")

    net = network_from_json(ws.network_json)
    spec = get_spec(ws.scenario)
    ctx_values = context_from_json(ws.context_json, net)
    variables = get_variable_info(spec, net, ws.mode)

    ctx_display: dict = {}
    from ctmsn.core.concept import Concept
    for k, v in ctx_values.items():
        ctx_display[k] = v.id if isinstance(v, Concept) else v

    return {
        "id": ws.id,
        "name": ws.name,
        "scenario": ws.scenario,
        "mode": ws.mode,
        "owner_id": ws.owner_id,
        "graph": serialize(net),
        "variables": variables,
        "context": ctx_display,
    }


@router.post("/workspaces/{workspace_id}/comments", response_model=CommentOut)
def add_comment(
    workspace_id: str,
    req: AddCommentReq,
    teacher: User = Depends(_teacher_dep),
    db: Session = Depends(get_db),
):
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")

    comment = Comment(workspace_id=workspace_id, author_id=teacher.id, text=req.text)
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return CommentOut(
        id=comment.id,
        author_id=comment.author_id,
        author_username=teacher.username,
        text=comment.text,
        created_at=comment.created_at.isoformat(),
    )


@router.get("/workspaces/{workspace_id}/comments", response_model=List[CommentOut])
def list_comments(
    workspace_id: str,
    teacher: User = Depends(_teacher_dep),
    db: Session = Depends(get_db),
):
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")

    comments = (
        db.query(Comment, User.username)
        .join(User, Comment.author_id == User.id)
        .filter(Comment.workspace_id == workspace_id)
        .order_by(Comment.created_at)
        .all()
    )
    return [
        CommentOut(
            id=c.id, author_id=c.author_id, author_username=uname,
            text=c.text, created_at=c.created_at.isoformat(),
        )
        for c, uname in comments
    ]

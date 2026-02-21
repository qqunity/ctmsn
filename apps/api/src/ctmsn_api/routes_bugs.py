from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ctmsn_api.auth import get_current_user, require_role
from ctmsn_api.config import ALGORITHM, SECRET_KEY
from ctmsn_api.database import get_db
from ctmsn_api.models import BugReport, BugStatus, Role, User, Workspace, _uuid_hex, _utcnow

router = APIRouter(tags=["bugs"])

_teacher_dep = require_role(Role.teacher)

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent.parent / "uploads" / "screenshots"


def _resolve_user_from_token(token: str | None, db: Session) -> User | None:
    """Resolve user from a JWT token string (for query-param auth)."""
    if not token:
        return None
    from jose import JWTError, jwt as jose_jwt
    try:
        payload = jose_jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") == "access":
            user_id = payload.get("sub")
            if user_id:
                return db.query(User).filter(User.id == user_id).first()
    except JWTError:
        pass
    return None


def _bug_to_dict(bug: BugReport, author_username: str, workspace_name: str | None) -> dict:
    return {
        "id": bug.id,
        "author_username": author_username,
        "workspace_id": bug.workspace_id,
        "workspace_name": workspace_name,
        "title": bug.title,
        "description": bug.description,
        "has_screenshot": bug.screenshot_path is not None,
        "status": bug.status.value if isinstance(bug.status, BugStatus) else bug.status,
        "created_at": bug.created_at.isoformat(),
    }


# ─── Student endpoints ────────────────────────────────────────

@router.post("/api/bugs")
async def create_bug(
    title: str = Form(...),
    description: str = Form(...),
    workspace_id: str | None = Form(None),
    screenshot: UploadFile | None = File(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if workspace_id:
        ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
        if not ws:
            raise HTTPException(status_code=404, detail="Workspace not found")

    bug_id = _uuid_hex()
    screenshot_path = None

    if screenshot and screenshot.filename:
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        ext = Path(screenshot.filename).suffix or ".png"
        filename = f"{bug_id}{ext}"
        filepath = UPLOAD_DIR / filename
        with open(filepath, "wb") as f:
            shutil.copyfileobj(screenshot.file, f)
        screenshot_path = str(filepath)

    bug = BugReport(
        id=bug_id,
        author_id=user.id,
        workspace_id=workspace_id or None,
        title=title,
        description=description,
        screenshot_path=screenshot_path,
    )
    db.add(bug)
    db.commit()
    db.refresh(bug)

    return _bug_to_dict(bug, user.username, None)


@router.get("/api/bugs/my")
def my_bugs(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(BugReport, User.username, Workspace.name)
        .join(User, BugReport.author_id == User.id)
        .outerjoin(Workspace, BugReport.workspace_id == Workspace.id)
        .filter(BugReport.author_id == user.id)
        .order_by(BugReport.created_at.desc())
        .all()
    )
    return [_bug_to_dict(bug, uname, wname) for bug, uname, wname in rows]


# ─── Teacher endpoints ────────────────────────────────────────

@router.get("/api/teacher/bugs")
def list_all_bugs(
    status_filter: str | None = None,
    teacher: User = Depends(_teacher_dep),
    db: Session = Depends(get_db),
):
    q = (
        db.query(BugReport, User.username, Workspace.name)
        .join(User, BugReport.author_id == User.id)
        .outerjoin(Workspace, BugReport.workspace_id == Workspace.id)
    )
    if status_filter and status_filter in ("open", "closed"):
        q = q.filter(BugReport.status == status_filter)
    rows = q.order_by(BugReport.created_at.desc()).all()
    return [_bug_to_dict(bug, uname, wname) for bug, uname, wname in rows]


class UpdateBugStatusReq(BaseModel):
    status: str


@router.patch("/api/teacher/bugs/{bug_id}")
def update_bug_status(
    bug_id: str,
    req: UpdateBugStatusReq,
    teacher: User = Depends(_teacher_dep),
    db: Session = Depends(get_db),
):
    if req.status not in ("open", "closed"):
        raise HTTPException(status_code=400, detail="Status must be 'open' or 'closed'")

    bug = db.query(BugReport).filter(BugReport.id == bug_id).first()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug report not found")

    bug.status = req.status
    bug.updated_at = _utcnow()
    db.commit()
    db.refresh(bug)

    author = db.query(User).filter(User.id == bug.author_id).first()
    ws = db.query(Workspace).filter(Workspace.id == bug.workspace_id).first() if bug.workspace_id else None
    return _bug_to_dict(bug, author.username if author else "", ws.name if ws else None)


@router.delete("/api/teacher/bugs/{bug_id}")
def delete_bug(
    bug_id: str,
    teacher: User = Depends(_teacher_dep),
    db: Session = Depends(get_db),
):
    bug = db.query(BugReport).filter(BugReport.id == bug_id).first()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug report not found")

    if bug.screenshot_path and os.path.exists(bug.screenshot_path):
        os.remove(bug.screenshot_path)

    db.delete(bug)
    db.commit()
    return {"ok": True}


# ─── Screenshot access ────────────────────────────────────────

@router.get("/api/bugs/{bug_id}/screenshot")
def get_screenshot(
    bug_id: str,
    token: str | None = Query(None),
    db: Session = Depends(get_db),
):
    user = _resolve_user_from_token(token, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    bug = db.query(BugReport).filter(BugReport.id == bug_id).first()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug report not found")

    if user.role != Role.teacher and bug.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    if not bug.screenshot_path or not os.path.exists(bug.screenshot_path):
        raise HTTPException(status_code=404, detail="Screenshot not found")

    return FileResponse(bug.screenshot_path)

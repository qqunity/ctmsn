from __future__ import annotations

from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ctmsn.core.concept import Concept
from ctmsn.core.predicate import Predicate
from ctmsn_api.auth import get_current_user
from ctmsn_api.database import create_tables, get_db
from ctmsn_api.models import Comment, User, Workspace
from ctmsn_api.ops import run_ops
from ctmsn_api.registry import get as get_spec, init_registry, list_specs
from ctmsn_api.routes_auth import router as auth_router
from ctmsn_api.routes_teacher import router as teacher_router
from ctmsn_api.serialize import serialize
from ctmsn_api.sessions import (
    SessionState,
    create_workspace,
    get_session,
    network_from_json,
    put_session,
)

app = FastAPI(title="CTnSS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(teacher_router)

init_registry()


@app.on_event("startup")
def on_startup():
    create_tables()


def check_workspace_access(workspace_id: str, user: User, db: Session) -> Workspace:
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    if ws.owner_id != user.id and user.role.value != "teacher":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return ws


@app.get("/api/scenarios")
def scenarios():
    return {"scenarios": list_specs()}


class LoadReq(BaseModel):
    scenario: str
    mode: Optional[str] = None
    derive: bool = True


@app.post("/api/session/load")
def load(
    req: LoadReq,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    spec = get_spec(req.scenario)
    net = spec.build(mode=req.mode) if req.mode else spec.build()

    workspace_id = create_workspace(user.id, req.scenario, req.mode, net, db)

    ops = run_ops(net, spec, derive=req.derive, mode=req.mode)
    return {
        "session_id": workspace_id,
        "scenario": req.scenario,
        "mode": req.mode,
        "graph": serialize(net),
        **ops,
    }


class RunReq(BaseModel):
    session_id: str
    derive: bool = True


@app.post("/api/run")
def run(
    req: RunReq,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_workspace_access(req.session_id, user, db)
    st = get_session(req.session_id, db)
    if not st:
        return {"error": "unknown session"}

    spec = get_spec(st.scenario)
    ops = run_ops(st.net, spec, derive=req.derive, mode=st.mode)
    return {
        "session_id": req.session_id,
        "scenario": st.scenario,
        "mode": st.mode,
        "graph": serialize(st.net),
        **ops,
    }


class AddConceptReq(BaseModel):
    session_id: str
    id: str
    label: str
    tags: list[str] = []


@app.post("/api/session/add_concept")
def add_concept(
    req: AddConceptReq,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_workspace_access(req.session_id, user, db)
    st = get_session(req.session_id, db)
    if not st:
        return {"error": "unknown session"}

    try:
        concept = Concept(id=req.id, label=req.label, tags=frozenset(req.tags))
        st.net.add_concept(concept)
        put_session(req.session_id, st, db)
        return {"ok": True, "graph": serialize(st.net)}
    except ValueError as e:
        return {"error": str(e)}


class AddPredicateReq(BaseModel):
    session_id: str
    name: str
    arity: int


@app.post("/api/session/add_predicate")
def add_predicate(
    req: AddPredicateReq,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_workspace_access(req.session_id, user, db)
    st = get_session(req.session_id, db)
    if not st:
        return {"error": "unknown session"}

    try:
        predicate = Predicate(name=req.name, arity=req.arity)
        st.net.add_predicate(predicate)
        put_session(req.session_id, st, db)
        return {"ok": True, "graph": serialize(st.net)}
    except ValueError as e:
        return {"error": str(e)}


class AddFactReq(BaseModel):
    session_id: str
    predicate: str
    args: list[str]


@app.post("/api/session/add_fact")
def add_fact(
    req: AddFactReq,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_workspace_access(req.session_id, user, db)
    st = get_session(req.session_id, db)
    if not st:
        return {"error": "unknown session"}

    try:
        args = tuple(st.net.concepts[cid] for cid in req.args)
        st.net.assert_fact(req.predicate, args)
        put_session(req.session_id, st, db)
        return {"ok": True, "graph": serialize(st.net)}
    except (KeyError, ValueError) as e:
        return {"error": str(e)}


@app.get("/api/workspaces")
def list_workspaces(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws_list = (
        db.query(Workspace)
        .filter(Workspace.owner_id == user.id)
        .order_by(Workspace.created_at.desc())
        .all()
    )
    return {
        "workspaces": [
            {
                "id": w.id,
                "scenario": w.scenario,
                "mode": w.mode,
                "created_at": w.created_at.isoformat(),
                "updated_at": w.updated_at.isoformat(),
            }
            for w in ws_list
        ]
    }


class AddCommentReq(BaseModel):
    text: str


@app.get("/api/workspaces/{workspace_id}/comments")
def workspace_comments(
    workspace_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_workspace_access(workspace_id, user, db)
    comments = (
        db.query(Comment, User.username)
        .join(User, Comment.author_id == User.id)
        .filter(Comment.workspace_id == workspace_id)
        .order_by(Comment.created_at)
        .all()
    )
    return {
        "comments": [
            {
                "id": c.id,
                "author_id": c.author_id,
                "author_username": uname,
                "text": c.text,
                "created_at": c.created_at.isoformat(),
            }
            for c, uname in comments
        ]
    }


@app.post("/api/workspaces/{workspace_id}/comments")
def add_workspace_comment(
    workspace_id: str,
    req: AddCommentReq,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_workspace_access(workspace_id, user, db)
    comment = Comment(workspace_id=workspace_id, author_id=user.id, text=req.text)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {
        "id": comment.id,
        "author_id": comment.author_id,
        "author_username": user.username,
        "text": comment.text,
        "created_at": comment.created_at.isoformat(),
    }

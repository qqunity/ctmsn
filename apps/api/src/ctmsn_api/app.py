from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ctmsn.core.concept import Concept
from ctmsn.core.predicate import Predicate
from ctmsn_api.auth import get_current_user
from ctmsn_api.database import create_tables, get_db, migrate_db
from ctmsn_api.models import Comment, User, Workspace
from ctmsn_api.ops import run_ops
from ctmsn_api.registry import get as get_spec, init_registry, list_specs
from ctmsn_api.routes_auth import router as auth_router
from ctmsn_api.routes_teacher import router as teacher_router
from ctmsn_api.serialize import serialize
from ctmsn_api.sessions import (
    SessionState,
    context_from_json,
    context_to_json,
    create_workspace,
    get_session,
    network_from_json,
    network_to_json,
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
    migrate_db()


def _count_user_workspaces(owner_id: str, scenario: str, db: Session) -> int:
    return (
        db.query(Workspace)
        .filter(
            Workspace.owner_id == owner_id,
            Workspace.scenario == scenario,
            Workspace.is_deleted.is_(None),
        )
        .count()
    )


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


# --- Session / Load ---

class LoadReq(BaseModel):
    scenario: str
    mode: Optional[str] = None
    derive: bool = True
    name: Optional[str] = None


@app.post("/api/session/load")
def load(
    req: LoadReq,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    spec = get_spec(req.scenario)
    net = spec.build(mode=req.mode) if req.mode else spec.build()

    if req.name:
        ws_name = req.name
    else:
        n = _count_user_workspaces(user.id, req.scenario, db) + 1
        ws_name = f"{req.scenario} #{n}"

    workspace_id = create_workspace(user.id, req.scenario, req.mode, net, db, name=ws_name)

    ops = run_ops(net, spec, derive=req.derive, mode=req.mode)
    return {
        "session_id": workspace_id,
        "name": ws_name,
        "scenario": req.scenario,
        "mode": req.mode,
        "graph": serialize(net),
        **ops,
    }


# --- Run ---

class RunReq(BaseModel):
    session_id: str
    derive: bool = True


@app.post("/api/run")
def run(
    req: RunReq,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws = check_workspace_access(req.session_id, user, db)
    st = get_session(req.session_id, db)
    if not st:
        return {"error": "unknown session"}

    spec = get_spec(st.scenario)
    ops = run_ops(st.net, spec, derive=req.derive, mode=st.mode, context_values=st.context_values)
    return {
        "session_id": req.session_id,
        "name": ws.name,
        "scenario": st.scenario,
        "mode": st.mode,
        "graph": serialize(st.net),
        **ops,
    }


# --- Set Variable ---

class SetVariableReq(BaseModel):
    session_id: str
    variable: str
    value: str


@app.post("/api/session/set_variable")
def set_variable(
    req: SetVariableReq,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws = check_workspace_access(req.session_id, user, db)
    st = get_session(req.session_id, db)
    if not st:
        raise HTTPException(status_code=404, detail="Session not found")

    spec = get_spec(st.scenario)

    # Resolve value: try concept first, then keep as string
    resolved_value: Any = req.value
    if req.value in st.net.concepts:
        resolved_value = st.net.concepts[req.value]

    # Validate via variables if available
    if spec.variables:
        import inspect
        sig = inspect.signature(spec.variables)
        params = list(sig.parameters.keys())
        if len(params) >= 1:
            variables_result = spec.variables(st.net)
        else:
            variables_result = spec.variables()

        from ctmsn.param.variable import Variable
        vars_obj = variables_result[0]
        found = False
        for attr_name in dir(vars_obj):
            val = getattr(vars_obj, attr_name, None)
            if isinstance(val, Variable) and val.name == req.variable:
                if not val.domain.contains(resolved_value):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Value '{req.value}' not in domain of '{req.variable}': {val.domain.describe()}",
                    )
                found = True
                break
        if not found:
            raise HTTPException(status_code=400, detail=f"Unknown variable '{req.variable}'")

    ctx_values = dict(st.context_values)
    ctx_values[req.variable] = resolved_value

    put_session(req.session_id, st, db, context_values=ctx_values)

    ops = run_ops(st.net, spec, derive=True, mode=st.mode, context_values=ctx_values)
    return {
        "session_id": req.session_id,
        "name": ws.name,
        "scenario": st.scenario,
        "mode": st.mode,
        "graph": serialize(st.net),
        **ops,
    }


# --- Network editing ---

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


# --- Workspaces ---

@app.get("/api/workspaces")
def list_workspaces(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws_list = (
        db.query(Workspace)
        .filter(Workspace.owner_id == user.id, Workspace.is_deleted.is_(None))
        .order_by(Workspace.created_at.desc())
        .all()
    )
    return {
        "workspaces": [
            {
                "id": w.id,
                "name": w.name,
                "scenario": w.scenario,
                "mode": w.mode,
                "created_at": w.created_at.isoformat(),
                "updated_at": w.updated_at.isoformat(),
            }
            for w in ws_list
        ]
    }


class RenameReq(BaseModel):
    name: str


@app.patch("/api/workspaces/{workspace_id}")
def rename_workspace(
    workspace_id: str,
    req: RenameReq,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws = check_workspace_access(workspace_id, user, db)
    ws.name = req.name
    db.commit()
    return {"ok": True, "id": ws.id, "name": ws.name}


@app.delete("/api/workspaces/{workspace_id}")
def delete_workspace(
    workspace_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws = check_workspace_access(workspace_id, user, db)
    ws.is_deleted = datetime.now(timezone.utc)
    db.commit()
    return {"ok": True}


@app.post("/api/workspaces/{workspace_id}/duplicate")
def duplicate_workspace(
    workspace_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws = check_workspace_access(workspace_id, user, db)
    new_name = f"{ws.name} (копия)" if ws.name else f"{ws.scenario} (копия)"
    new_ws = Workspace(
        owner_id=user.id,
        scenario=ws.scenario,
        mode=ws.mode,
        name=new_name,
        network_json=ws.network_json,
        context_json=ws.context_json,
    )
    db.add(new_ws)
    db.commit()
    db.refresh(new_ws)
    return {"id": new_ws.id, "name": new_ws.name}


@app.get("/api/workspaces/{workspace_id}/export")
def export_workspace(
    workspace_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws = check_workspace_access(workspace_id, user, db)
    import json
    return {
        "scenario": ws.scenario,
        "mode": ws.mode,
        "name": ws.name,
        "network": json.loads(ws.network_json),
        "context": json.loads(ws.context_json),
    }


class ImportReq(BaseModel):
    data: dict


@app.post("/api/workspaces/import")
def import_workspace(
    req: ImportReq,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    import json
    d = req.data
    scenario = d.get("scenario", "")
    mode = d.get("mode")
    name = d.get("name", f"{scenario} (импорт)")
    network_json = json.dumps(d.get("network", {}))
    context_json = json.dumps(d.get("context", {}))

    ws = Workspace(
        owner_id=user.id,
        scenario=scenario,
        mode=mode,
        name=name,
        network_json=network_json,
        context_json=context_json,
    )
    db.add(ws)
    db.commit()
    db.refresh(ws)
    return {"id": ws.id, "name": ws.name}


# --- Comments ---

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

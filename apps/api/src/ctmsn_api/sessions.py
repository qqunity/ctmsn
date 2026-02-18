from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Optional

from sqlalchemy.orm import Session

from ctmsn.core.concept import Concept
from ctmsn.core.network import SemanticNetwork
from ctmsn.core.predicate import Predicate
from ctmsn.io.serializer import dump_network
from ctmsn_api.models import NetworkSnapshot, Workspace


@dataclass
class SessionState:
    scenario: str
    mode: Optional[str]
    net: SemanticNetwork
    context_values: dict[str, Any] = field(default_factory=dict)


def network_to_json(net: SemanticNetwork) -> str:
    return json.dumps(dump_network(net))


def network_from_json(data: str) -> SemanticNetwork:
    raw = json.loads(data) if isinstance(data, str) else data
    net = SemanticNetwork()

    for cid, cdata in raw.get("concepts", {}).items():
        net.add_concept(Concept(
            id=cdata["id"],
            label=cdata.get("label"),
            tags=frozenset(cdata.get("tags", [])),
            meta=cdata.get("meta", {}),
        ))

    for pname, pdata in raw.get("predicates", {}).items():
        roles = tuple(pdata.get("roles", []))
        net.add_predicate(Predicate(name=pdata["name"], arity=pdata["arity"], roles=roles))

    for fdata in raw.get("facts", []):
        pred_name = fdata["predicate"]
        args = tuple(net.concepts[a] if a in net.concepts else a for a in fdata["args"])
        net.assert_fact(pred_name, args)

    return net


def context_to_json(ctx_values: dict[str, Any], net: SemanticNetwork) -> str:
    serialized: dict[str, Any] = {}
    for key, val in ctx_values.items():
        if isinstance(val, Concept):
            serialized[key] = {"__concept__": val.id}
        else:
            serialized[key] = val
    return json.dumps(serialized)


def context_from_json(data: str, net: SemanticNetwork) -> dict[str, Any]:
    if not data or data == "{}":
        return {}
    try:
        raw = json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return {}
    result: dict[str, Any] = {}
    for key, val in raw.items():
        try:
            if isinstance(val, dict) and "__concept__" in val:
                cid = val["__concept__"]
                if cid in net.concepts:
                    result[key] = net.concepts[cid]
            else:
                result[key] = val
        except Exception:
            pass
    return result


def get_session(workspace_id: str, db: Session) -> Optional[SessionState]:
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        return None
    net = network_from_json(ws.network_json)
    ctx_values = context_from_json(ws.context_json, net)
    return SessionState(scenario=ws.scenario, mode=ws.mode, net=net, context_values=ctx_values)


def put_session(
    workspace_id: str,
    st: SessionState,
    db: Session,
    context_values: dict[str, Any] | None = None,
) -> None:
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if ws:
        ws.network_json = network_to_json(st.net)
        ws.scenario = st.scenario
        ws.mode = st.mode
        if context_values is not None:
            ws.context_json = context_to_json(context_values, st.net)
        db.commit()


def create_workspace(
    owner_id: str,
    scenario: str,
    mode: str | None,
    net: SemanticNetwork,
    db: Session,
    name: str = "",
    context_values: dict[str, Any] | None = None,
) -> str:
    ctx_json = context_to_json(context_values or {}, net)
    ws = Workspace(
        owner_id=owner_id,
        scenario=scenario,
        mode=mode,
        name=name,
        network_json=network_to_json(net),
        context_json=ctx_json,
    )
    db.add(ws)
    db.commit()
    db.refresh(ws)
    return ws.id


MAX_UNDO = 15


def push_undo(workspace_id: str, db: Session, action: str = "") -> None:
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        return
    snap = NetworkSnapshot(
        workspace_id=workspace_id,
        network_json=ws.network_json,
        context_json=ws.context_json,
        action=action,
        stack="undo",
    )
    db.add(snap)
    db.query(NetworkSnapshot).filter(
        NetworkSnapshot.workspace_id == workspace_id,
        NetworkSnapshot.stack == "redo",
    ).delete()
    undo_count = (
        db.query(NetworkSnapshot)
        .filter(NetworkSnapshot.workspace_id == workspace_id, NetworkSnapshot.stack == "undo")
        .count()
    )
    if undo_count > MAX_UNDO:
        oldest = (
            db.query(NetworkSnapshot)
            .filter(NetworkSnapshot.workspace_id == workspace_id, NetworkSnapshot.stack == "undo")
            .order_by(NetworkSnapshot.created_at.asc())
            .limit(undo_count - MAX_UNDO)
            .all()
        )
        for s in oldest:
            db.delete(s)
    db.flush()


def do_undo(workspace_id: str, db: Session) -> bool:
    latest = (
        db.query(NetworkSnapshot)
        .filter(NetworkSnapshot.workspace_id == workspace_id, NetworkSnapshot.stack == "undo")
        .order_by(NetworkSnapshot.created_at.desc())
        .first()
    )
    if not latest:
        return False
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        return False
    redo_snap = NetworkSnapshot(
        workspace_id=workspace_id,
        network_json=ws.network_json,
        context_json=ws.context_json,
        action=latest.action,
        stack="redo",
    )
    db.add(redo_snap)
    ws.network_json = latest.network_json
    ws.context_json = latest.context_json
    db.delete(latest)
    db.commit()
    return True


def do_redo(workspace_id: str, db: Session) -> bool:
    latest = (
        db.query(NetworkSnapshot)
        .filter(NetworkSnapshot.workspace_id == workspace_id, NetworkSnapshot.stack == "redo")
        .order_by(NetworkSnapshot.created_at.desc())
        .first()
    )
    if not latest:
        return False
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        return False
    undo_snap = NetworkSnapshot(
        workspace_id=workspace_id,
        network_json=ws.network_json,
        context_json=ws.context_json,
        action=latest.action,
        stack="undo",
    )
    db.add(undo_snap)
    ws.network_json = latest.network_json
    ws.context_json = latest.context_json
    db.delete(latest)
    db.commit()
    return True


def get_history_status(workspace_id: str, db: Session) -> dict:
    undo_count = (
        db.query(NetworkSnapshot)
        .filter(NetworkSnapshot.workspace_id == workspace_id, NetworkSnapshot.stack == "undo")
        .count()
    )
    redo_count = (
        db.query(NetworkSnapshot)
        .filter(NetworkSnapshot.workspace_id == workspace_id, NetworkSnapshot.stack == "redo")
        .count()
    )
    return {
        "can_undo": undo_count > 0,
        "can_redo": redo_count > 0,
        "undo_count": undo_count,
        "redo_count": redo_count,
    }

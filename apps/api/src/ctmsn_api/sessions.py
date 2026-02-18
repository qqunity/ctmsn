from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional

from sqlalchemy.orm import Session

from ctmsn.core.concept import Concept
from ctmsn.core.network import SemanticNetwork
from ctmsn.core.predicate import Predicate
from ctmsn.io.serializer import dump_network
from ctmsn_api.models import Workspace


@dataclass
class SessionState:
    scenario: str
    mode: Optional[str]
    net: SemanticNetwork


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
        args = tuple(net.concepts[a] for a in fdata["args"])
        net.assert_fact(pred_name, args)

    return net


def get_session(workspace_id: str, db: Session) -> Optional[SessionState]:
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        return None
    net = network_from_json(ws.network_json)
    return SessionState(scenario=ws.scenario, mode=ws.mode, net=net)


def put_session(workspace_id: str, st: SessionState, db: Session) -> None:
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if ws:
        ws.network_json = network_to_json(st.net)
        ws.scenario = st.scenario
        ws.mode = st.mode
        db.commit()


def create_workspace(owner_id: str, scenario: str, mode: str | None, net: SemanticNetwork, db: Session) -> str:
    ws = Workspace(
        owner_id=owner_id,
        scenario=scenario,
        mode=mode,
        network_json=network_to_json(net),
    )
    db.add(ws)
    db.commit()
    db.refresh(ws)
    return ws.id

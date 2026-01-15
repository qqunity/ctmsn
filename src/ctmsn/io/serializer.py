from __future__ import annotations
from dataclasses import asdict
from typing import Any, Dict

from ctmsn.core.network import SemanticNetwork
from ctmsn.param.context import Context


def dump_network(net: SemanticNetwork) -> Dict[str, Any]:
    return {
        "concepts": {cid: {"id": c.id, "label": c.label, "tags": list(c.tags), "meta": dict(c.meta)} for cid, c in net.concepts.items()},
        "predicates": {name: {"name": p.name, "arity": p.arity, "roles": list(p.roles)} for name, p in net.predicates.items()},
        "facts": [{"predicate": f.predicate, "args": [getattr(a, "id", a) for a in f.args]} for f in net.facts()],
    }


def dump_context(ctx: Context) -> Dict[str, Any]:
    return {"values": ctx.as_dict()}

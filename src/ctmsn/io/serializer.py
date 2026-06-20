from __future__ import annotations
from typing import Any, Dict

from ctmsn.core.concept import Concept
from ctmsn.core.network import SemanticNetwork
from ctmsn.core.predicate import Predicate
from ctmsn.param.context import Context


def dump_network(net: SemanticNetwork) -> Dict[str, Any]:
    return {
        "concepts": {cid: {"id": c.id, "label": c.label, "tags": list(c.tags), "meta": dict(c.meta)} for cid, c in net.concepts.items()},
        "predicates": {name: {"name": p.name, "arity": p.arity, "roles": list(p.roles)} for name, p in net.predicates.items()},
        "facts": [{"predicate": f.predicate, "args": [getattr(a, "id", a) for a in f.args]} for f in net.facts()],
    }


def load_network(data: Dict[str, Any], strict: bool = True) -> SemanticNetwork:
    """Восстановить SemanticNetwork из dump_network (round-trip).

    strict=False пропускает факты, вызывающие противоречие (has_*/lacks_*),
    вместо выброса исключения.
    """
    net = SemanticNetwork()
    for cdata in data.get("concepts", {}).values():
        net.add_concept(Concept(
            id=cdata["id"],
            label=cdata.get("label"),
            tags=frozenset(cdata.get("tags", [])),
            meta=dict(cdata.get("meta", {})),
        ))
    for pdata in data.get("predicates", {}).values():
        net.add_predicate(Predicate(
            name=pdata["name"],
            arity=pdata["arity"],
            roles=tuple(pdata.get("roles", [])),
        ))
    for fdata in data.get("facts", []):
        args = tuple(net.concepts[a] if a in net.concepts else a for a in fdata["args"])
        try:
            net.assert_fact(fdata["predicate"], args)
        except ValueError:
            if strict:
                raise
    return net


def dump_context(ctx: Context) -> Dict[str, Any]:
    values: Dict[str, Any] = {}
    for name, val in ctx.as_dict().items():
        values[name] = {"__concept__": val.id} if isinstance(val, Concept) else val
    return {"values": values}


def load_context(data: Dict[str, Any], net: SemanticNetwork | None = None) -> Context:
    """Восстановить Context из dump_context, разрешая концепты по сети."""
    raw = data.get("values", {}) if data else {}
    resolved: Dict[str, Any] = {}
    for name, val in raw.items():
        if isinstance(val, dict) and "__concept__" in val:
            cid = val["__concept__"]
            resolved[name] = net.concepts[cid] if (net and cid in net.concepts) else cid
        else:
            resolved[name] = val
    return Context(_values=resolved)

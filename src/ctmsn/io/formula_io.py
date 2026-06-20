"""Сериализация формул и термов в dict и обратно (zero-dependency).

Формат совместим с формулами веб-платформы (formula_serde): формула — объект
с полем "type", терм — объект с полем "kind" (concept|variable|literal).
"""

from __future__ import annotations

from typing import Any

from ctmsn.core.concept import Concept
from ctmsn.core.network import SemanticNetwork
from ctmsn.logic.formula import And, EqAtom, FactAtom, Formula, Implies, Not, Or
from ctmsn.param.domain import PredicateDomain
from ctmsn.param.variable import Variable


def _any_domain() -> PredicateDomain:
    return PredicateDomain(fn=lambda _: True, name="any")


def term_to_dict(term: Any) -> dict[str, Any]:
    if isinstance(term, Concept):
        return {"kind": "concept", "id": term.id}
    if isinstance(term, Variable):
        return {"kind": "variable", "name": term.name}
    return {"kind": "literal", "value": term}


def term_from_dict(
    data: dict[str, Any],
    net: SemanticNetwork | None,
    var_map: dict[str, Variable] | None = None,
) -> Any:
    kind = data.get("kind")
    if kind == "concept":
        cid = data["id"]
        if net is not None and cid in net.concepts:
            return net.concepts[cid]
        return Concept(id=cid, label=cid)
    if kind == "variable":
        name = data["name"]
        if var_map and name in var_map:
            return var_map[name]
        return Variable(name=name, domain=_any_domain())
    if kind == "literal":
        return data["value"]
    raise ValueError(f"Unknown term kind: {kind!r}")


def formula_to_dict(formula: Formula) -> dict[str, Any]:
    if isinstance(formula, FactAtom):
        return {
            "type": "FactAtom",
            "predicate": formula.predicate,
            "args": [term_to_dict(a) for a in formula.args],
        }
    if isinstance(formula, EqAtom):
        return {"type": "EqAtom", "left": term_to_dict(formula.left), "right": term_to_dict(formula.right)}
    if isinstance(formula, Not):
        return {"type": "Not", "inner": formula_to_dict(formula.inner)}
    if isinstance(formula, And):
        return {"type": "And", "items": [formula_to_dict(i) for i in formula.items]}
    if isinstance(formula, Or):
        return {"type": "Or", "items": [formula_to_dict(i) for i in formula.items]}
    if isinstance(formula, Implies):
        return {"type": "Implies", "left": formula_to_dict(formula.left), "right": formula_to_dict(formula.right)}
    raise ValueError(f"Unknown formula type: {type(formula)}")


def formula_from_dict(
    data: dict[str, Any],
    net: SemanticNetwork | None,
    var_map: dict[str, Variable] | None = None,
) -> Formula:
    ftype = data.get("type")
    if ftype == "FactAtom":
        args = tuple(term_from_dict(a, net, var_map) for a in data.get("args", []))
        return FactAtom(predicate=data["predicate"], args=args)
    if ftype == "EqAtom":
        return EqAtom(
            left=term_from_dict(data["left"], net, var_map),
            right=term_from_dict(data["right"], net, var_map),
        )
    if ftype == "Not":
        return Not(inner=formula_from_dict(data["inner"], net, var_map))
    if ftype == "And":
        return And(items=tuple(formula_from_dict(i, net, var_map) for i in data.get("items", [])))
    if ftype == "Or":
        return Or(items=tuple(formula_from_dict(i, net, var_map) for i in data.get("items", [])))
    if ftype == "Implies":
        return Implies(
            left=formula_from_dict(data["left"], net, var_map),
            right=formula_from_dict(data["right"], net, var_map),
        )
    raise ValueError(f"Unknown formula type: {ftype!r}")

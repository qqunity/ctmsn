from __future__ import annotations

from typing import Any

from ctmsn.core.concept import Concept
from ctmsn.core.network import SemanticNetwork
from ctmsn.logic.formula import And, EqAtom, FactAtom, Formula, Implies, Not, Or
from ctmsn.param.variable import Variable


def _term_from_json(
    data: dict[str, Any],
    net: SemanticNetwork,
    var_map: dict[str, Variable],
) -> Any:
    kind = data.get("kind")
    if kind == "concept":
        cid = data["id"]
        if cid in net.concepts:
            return net.concepts[cid]
        return Concept(id=cid, label=cid)
    if kind == "variable":
        name = data["name"]
        if name in var_map:
            return var_map[name]
        return Variable(name=name, domain=_any_domain())
    if kind == "literal":
        return data["value"]
    raise ValueError(f"Unknown term kind: {kind}")


def _any_domain():
    from ctmsn.param.domain import PredicateDomain
    return PredicateDomain(fn=lambda _: True, name="any")


def formula_from_json(
    data: dict[str, Any],
    net: SemanticNetwork,
    var_map: dict[str, Variable],
) -> Formula:
    ftype = data.get("type")
    if ftype == "FactAtom":
        args = tuple(_term_from_json(a, net, var_map) for a in data.get("args", []))
        return FactAtom(predicate=data["predicate"], args=args)
    if ftype == "EqAtom":
        left = _term_from_json(data["left"], net, var_map)
        right = _term_from_json(data["right"], net, var_map)
        return EqAtom(left=left, right=right)
    if ftype == "Not":
        return Not(inner=formula_from_json(data["inner"], net, var_map))
    if ftype == "And":
        items = tuple(formula_from_json(i, net, var_map) for i in data.get("items", []))
        return And(items=items)
    if ftype == "Or":
        items = tuple(formula_from_json(i, net, var_map) for i in data.get("items", []))
        return Or(items=items)
    if ftype == "Implies":
        left = formula_from_json(data["left"], net, var_map)
        right = formula_from_json(data["right"], net, var_map)
        return Implies(left=left, right=right)
    raise ValueError(f"Unknown formula type: {ftype}")


def _term_to_json(term: Any) -> dict[str, Any]:
    if isinstance(term, Concept):
        return {"kind": "concept", "id": term.id}
    if isinstance(term, Variable):
        return {"kind": "variable", "name": term.name}
    return {"kind": "literal", "value": term}


def formula_to_json(formula: Formula) -> dict[str, Any]:
    if isinstance(formula, FactAtom):
        return {
            "type": "FactAtom",
            "predicate": formula.predicate,
            "args": [_term_to_json(a) for a in formula.args],
        }
    if isinstance(formula, EqAtom):
        return {
            "type": "EqAtom",
            "left": _term_to_json(formula.left),
            "right": _term_to_json(formula.right),
        }
    if isinstance(formula, Not):
        return {"type": "Not", "inner": formula_to_json(formula.inner)}
    if isinstance(formula, And):
        return {"type": "And", "items": [formula_to_json(i) for i in formula.items]}
    if isinstance(formula, Or):
        return {"type": "Or", "items": [formula_to_json(i) for i in formula.items]}
    if isinstance(formula, Implies):
        return {
            "type": "Implies",
            "left": formula_to_json(formula.left),
            "right": formula_to_json(formula.right),
        }
    raise ValueError(f"Unknown formula type: {type(formula)}")


def _term_to_text(term: Any) -> str:
    if isinstance(term, Concept):
        return term.id
    if isinstance(term, Variable):
        return term.name
    return repr(term)


def formula_to_text(formula: Formula) -> str:
    if isinstance(formula, FactAtom):
        args_str = ", ".join(_term_to_text(a) for a in formula.args)
        return f'FactAtom("{formula.predicate}", {args_str})'
    if isinstance(formula, EqAtom):
        return f"EqAtom({_term_to_text(formula.left)}, {_term_to_text(formula.right)})"
    if isinstance(formula, Not):
        return f"Not({formula_to_text(formula.inner)})"
    if isinstance(formula, And):
        items_str = ", ".join(formula_to_text(i) for i in formula.items)
        return f"And({items_str})"
    if isinstance(formula, Or):
        items_str = ", ".join(formula_to_text(i) for i in formula.items)
        return f"Or({items_str})"
    if isinstance(formula, Implies):
        return f"Implies({formula_to_text(formula.left)}, {formula_to_text(formula.right)})"
    return str(formula)

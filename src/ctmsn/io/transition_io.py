"""Сериализация правил переходов и инвариантов в dict и обратно (zero-dependency)."""

from __future__ import annotations

from typing import Any

from ctmsn.core.network import SemanticNetwork
from ctmsn.forcing.conditions import Conditions
from ctmsn.param.variable import Variable
from ctmsn.transition.rule import AddFact, FactOp, RetractFact, TransitionRule
from ctmsn.io.formula_io import formula_from_dict, formula_to_dict


def effect_to_list(effect) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for op in effect:
        kind = "add" if isinstance(op, AddFact) else "retract"
        out.append({"op": kind, "predicate": op.predicate, "args": list(op.args)})
    return out


def effect_from_list(data: list[dict[str, Any]]) -> tuple[FactOp, ...]:
    ops: list[FactOp] = []
    for op in data or []:
        pred = op.get("predicate")
        if not pred:
            continue
        args = tuple(op.get("args", []))
        if op.get("op") == "add":
            ops.append(AddFact(predicate=pred, args=args))
        elif op.get("op") == "retract":
            ops.append(RetractFact(predicate=pred, args=args))
    return tuple(ops)


def rule_to_dict(rule: TransitionRule) -> dict[str, Any]:
    return {
        "name": rule.name,
        "guard": formula_to_dict(rule.guard),
        "effect": effect_to_list(rule.effect),
        "priority": rule.priority,
        "on_event": rule.on_event,
    }


def rule_from_dict(
    data: dict[str, Any],
    net: SemanticNetwork | None,
    var_map: dict[str, Variable] | None = None,
) -> TransitionRule:
    return TransitionRule(
        name=data["name"],
        guard=formula_from_dict(data["guard"], net, var_map),
        effect=effect_from_list(data.get("effect", [])),
        priority=int(data.get("priority", 0)),
        on_event=data.get("on_event"),
    )


def invariants_to_list(conditions: Conditions) -> list[dict[str, Any]]:
    return [formula_to_dict(f) for f in conditions.items]


def invariants_from_list(
    data: list[dict[str, Any]],
    net: SemanticNetwork | None,
    var_map: dict[str, Variable] | None = None,
) -> Conditions:
    return Conditions(items=tuple(formula_from_dict(f, net, var_map) for f in data or []))

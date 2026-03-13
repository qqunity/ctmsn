from __future__ import annotations

from ctmsn.logic.formula import FactAtom, Formula
from ctmsn.core.network import SemanticNetwork
from ctmsn.scenarios.lab5_inheritance.params import build_variables


def build_goal(net: SemanticNetwork) -> Formula:
    ability_swim = net.concepts["ability_swim"]
    v, _ = build_variables(net)

    return FactAtom("has_ability", (v.species, ability_swim))

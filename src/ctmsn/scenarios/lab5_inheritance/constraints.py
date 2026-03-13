from __future__ import annotations

from ctmsn.logic.formula import FactAtom
from ctmsn.forcing.conditions import Conditions
from ctmsn.core.network import SemanticNetwork


def build_conditions(net: SemanticNetwork) -> Conditions:
    penguin = net.concepts["penguin"]
    bird = net.concepts["bird"]
    ability_fly = net.concepts["ability_fly"]

    c1 = FactAtom("isa", (penguin, bird))
    c2 = FactAtom("has_ability", (penguin, ability_fly))

    return Conditions().add(c1, c2)

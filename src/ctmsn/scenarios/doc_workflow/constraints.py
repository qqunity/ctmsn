from __future__ import annotations

from ctmsn.core.network import SemanticNetwork
from ctmsn.forcing.conditions import Conditions
from ctmsn.logic.formula import FactAtom, Not


def build_conditions(net: SemanticNetwork) -> Conditions:
    """Условия форсирования: документ не отклонён и имеет назначенного рецензента."""
    doc = net.concepts["doc"]
    rejected = net.concepts["rejected"]
    alice = net.concepts["alice"]

    c1 = Not(FactAtom("status", (doc, rejected)))
    c2 = FactAtom("assigned", (doc, alice))

    return Conditions().add(c1, c2)

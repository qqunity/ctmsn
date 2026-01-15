from __future__ import annotations

from ctmsn.logic.formula import And, FactAtom
from ctmsn.core.network import SemanticNetwork


def build_goal(net: SemanticNetwork):
    A = net.concepts["A"]

    phi = And(
        (
            FactAtom("acts_like", (A, "jf")),
            FactAtom("acts_like", (A, "j")),
            FactAtom("acts_like", (A, "s")),
        )
    )
    return phi

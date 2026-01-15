from __future__ import annotations

from ctmsn.logic.formula import And, FactAtom, Not
from ctmsn.forcing.conditions import Conditions
from ctmsn.core.network import SemanticNetwork


def build_conditions(net: SemanticNetwork) -> Conditions:
    A = net.concepts["A"]
    T = net.concepts["T"]
    T_plus = net.concepts["T_plus"]
    T_minus = net.concepts["T_minus"]

    c1 = FactAtom("in", (T_minus, T))

    c2 = Not(FactAtom("in", (T_minus, T_plus)))

    c3 = FactAtom("comp", ("h", "g", "j"))
    c4 = FactAtom("comp", ("h", "not-g", "s"))
    c5 = FactAtom("comp", ("sf", "r", "jf"))

    return Conditions().add(c1, c2, c3, c4, c5)

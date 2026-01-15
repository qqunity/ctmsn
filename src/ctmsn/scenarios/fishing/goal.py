from __future__ import annotations

from ctmsn.logic.formula import And, FactAtom


def build_goal():
    return And((
        FactAtom("comp2", ("h", "g_minus", "s")),
        FactAtom("comp2", ("h", "g_plus", "j")),
        FactAtom("comp2", ("s", "catch", "j")),
        FactAtom("compN", ("hook+∘fake+∘eat∘sf", "catch_sf")),
    ))

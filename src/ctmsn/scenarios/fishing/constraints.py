from __future__ import annotations

from ctmsn.forcing.conditions import Conditions
from ctmsn.logic.formula import FactAtom


def build_conditions() -> Conditions:
    return Conditions().add(
        # g- ∘ h = s
        FactAtom("comp2", ("h", "g_minus", "s")),
        # g+ ∘ h = j
        FactAtom("comp2", ("h", "g_plus", "j")),
        # catch ∘ s = j
        FactAtom("comp2", ("s", "catch", "j")),
        # hook+ ∘ fake+ ∘ eat ∘ sf = catch ∘ sf
        FactAtom("compN", ("hook+∘fake+∘eat∘sf", "catch_sf")),
    )

from __future__ import annotations

from ctmsn.logic.formula import FactAtom
from ctmsn.forcing.conditions import Conditions


def build_conditions(mode: str = "sun") -> Conditions:
    if mode == "sun":
        return Conditions().add(
            FactAtom("comp", ("sun_before", "below", "sunset")),
            FactAtom("comp", ("sun_after", "above", "sunrise")),
            FactAtom("comp", ("sun1_before", "below_h", "sunset_h")),
            FactAtom("comp", ("sun1_after", "above_h", "sunrise_h")),
        )

    return Conditions().add(
        FactAtom("comp", ("h_before", "g_minus", "h_minus")),
        FactAtom("comp", ("h_after", "g_plus", "h_plus")),
    )

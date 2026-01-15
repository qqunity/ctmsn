from __future__ import annotations

from ctmsn.logic.formula import And, FactAtom


def build_goal(mode: str = "sun"):
    if mode == "sun":
        return And((
            FactAtom("comp", ("sun_before", "below", "sunset")),
            FactAtom("comp", ("sun_after", "above", "sunrise")),
        ))
    return And((
        FactAtom("comp", ("h_before", "g_minus", "h_minus")),
        FactAtom("comp", ("h_after", "g_plus", "h_plus")),
    ))

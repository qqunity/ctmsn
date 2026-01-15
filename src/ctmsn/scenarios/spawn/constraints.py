from __future__ import annotations

from ctmsn.forcing.conditions import Conditions
from ctmsn.logic.formula import FactAtom


def build_conditions() -> Conditions:
    """
    Canonical equalities from the text.
    """
    return Conditions().add(
        # spawner = not-eat ∘ fish
        FactAtom("comp2", ("fish", "not_eat", "spawner")),
        # milter  = eat ∘ fish
        FactAtom("comp2", ("fish", "eat", "milter")),

        # push ∘ milter_f = spawner_f  (i.e. comp2(milter_f, push, spawner_f))
        FactAtom("comp2", ("milter_f", "push", "spawner_f")),

        # rethink ∘ spawner_f = milter_f
        FactAtom("comp2", ("spawner_f", "rethink", "milter_f")),

        # rethink ∘ push ∘ milter_f = milter_f
        FactAtom("compN", ("rethink∘push∘milter_f", "milter_f")),

        # (rethink ∘ spawner_f)_e = (milter_f)_e
        FactAtom("compN", ("(rethink∘spawner_f)_e", "milter_fe")),
    )

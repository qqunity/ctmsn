from __future__ import annotations

from ctmsn.logic.formula import And, FactAtom


def build_goal():
    return And((
        FactAtom("comp2", ("fish", "not_eat", "spawner")),
        FactAtom("comp2", ("fish", "eat", "milter")),
        FactAtom("comp2", ("milter_f", "push", "spawner_f")),
        FactAtom("comp2", ("spawner_f", "rethink", "milter_f")),
        FactAtom("compN", ("rethink∘push∘milter_f", "milter_f")),
        FactAtom("compN", ("(rethink∘spawner_f)_e", "milter_fe")),
    ))

from __future__ import annotations

from ctmsn.logic.formula import And, FactAtom
from ctmsn.core.network import SemanticNetwork


def build_goal(net: SemanticNetwork) -> And:
    petrov = net.concepts["petrov"]
    course_db = net.concepts["course_db"]
    dept_cs = net.concepts["dept_cs"]
    ivanov = net.concepts["ivanov"]

    phi = And(
        (
            FactAtom("enrolled_in", (petrov, course_db)),
            FactAtom("studies_at", (petrov, dept_cs)),
            FactAtom("teaches", (ivanov, course_db)),
        )
    )
    return phi

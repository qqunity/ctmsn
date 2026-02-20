from __future__ import annotations

from ctmsn.logic.formula import FactAtom, Not
from ctmsn.forcing.conditions import Conditions
from ctmsn.core.network import SemanticNetwork


def build_conditions(net: SemanticNetwork) -> Conditions:
    dept_cs = net.concepts["dept_cs"]
    university = net.concepts["university"]
    ivanov = net.concepts["ivanov"]
    petrov = net.concepts["petrov"]
    course_db = net.concepts["course_db"]

    c1 = FactAtom("belongs_to", (dept_cs, university))
    c2 = FactAtom("works_at", (ivanov, dept_cs))
    c3 = Not(FactAtom("teaches", (petrov, course_db)))

    return Conditions().add(c1, c2, c3)

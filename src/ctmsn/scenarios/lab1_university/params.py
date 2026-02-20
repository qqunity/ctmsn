from __future__ import annotations

from dataclasses import dataclass

from ctmsn.param.domain import EnumDomain
from ctmsn.param.variable import Variable
from ctmsn.param.context import Context
from ctmsn.core.network import SemanticNetwork


@dataclass(frozen=True)
class Lab1Vars:
    student: Variable
    course: Variable
    teacher: Variable


def build_variables(net: SemanticNetwork) -> tuple[Lab1Vars, Context]:
    petrov = net.concepts["petrov"]
    course_db = net.concepts["course_db"]
    course_ai = net.concepts["course_ai"]
    ivanov = net.concepts["ivanov"]

    v = Lab1Vars(
        student=Variable("student", EnumDomain((petrov,))),
        course=Variable("course", EnumDomain((course_db, course_ai))),
        teacher=Variable("teacher", EnumDomain((ivanov,))),
    )

    ctx0 = Context()
    ctx0.set(v.course, course_db)

    return v, ctx0

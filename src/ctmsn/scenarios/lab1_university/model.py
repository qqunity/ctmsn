from __future__ import annotations

from ctmsn.core.concept import Concept
from ctmsn.core.predicate import Predicate
from ctmsn.core.network import SemanticNetwork


def build_network() -> SemanticNetwork:
    """
    Предметная область «Университет».
    6 концептов, 5 бинарных предикатов, 7 фактов.
    """

    net = SemanticNetwork()

    university = Concept("university", "Университет")
    dept_cs = Concept("dept_cs", "Кафедра ИВТ")
    course_db = Concept("course_db", "Базы данных")
    course_ai = Concept("course_ai", "Искусственный интеллект")
    ivanov = Concept("ivanov", "Преподаватель Иванов")
    petrov = Concept("petrov", "Студент Петров")

    for c in (university, dept_cs, course_db, course_ai, ivanov, petrov):
        net.add_concept(c)

    net.add_predicate(Predicate("belongs_to", 2, roles=("part", "whole")))
    net.add_predicate(Predicate("teaches", 2, roles=("teacher", "course")))
    net.add_predicate(Predicate("enrolled_in", 2, roles=("student", "course")))
    net.add_predicate(Predicate("works_at", 2, roles=("person", "place")))
    net.add_predicate(Predicate("studies_at", 2, roles=("student", "department")))

    net.assert_fact("belongs_to", (dept_cs, university))
    net.assert_fact("works_at", (ivanov, dept_cs))
    net.assert_fact("teaches", (ivanov, course_db))
    net.assert_fact("teaches", (ivanov, course_ai))
    net.assert_fact("enrolled_in", (petrov, course_db))
    net.assert_fact("enrolled_in", (petrov, course_ai))
    net.assert_fact("studies_at", (petrov, dept_cs))

    net.validate()
    return net

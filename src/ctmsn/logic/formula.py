from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple

from ctmsn.logic.terms import Term


class Formula:
    pass


@dataclass(frozen=True)
class FactAtom(Formula):
    predicate: str
    args: Tuple[Term, ...]


@dataclass(frozen=True)
class EqAtom(Formula):
    left: Term
    right: Term


@dataclass(frozen=True)
class Not(Formula):
    inner: Formula


@dataclass(frozen=True)
class And(Formula):
    items: Tuple[Formula, ...]


@dataclass(frozen=True)
class Or(Formula):
    items: Tuple[Formula, ...]


@dataclass(frozen=True)
class Implies(Formula):
    left: Formula
    right: Formula


def collect_variables(f: Formula) -> frozenset:
    from ctmsn.param.variable import Variable

    result: set[Variable] = set()

    def _collect(formula: Formula) -> None:
        if isinstance(formula, FactAtom):
            for a in formula.args:
                if isinstance(a, Variable):
                    result.add(a)
        elif isinstance(formula, EqAtom):
            if isinstance(formula.left, Variable):
                result.add(formula.left)
            if isinstance(formula.right, Variable):
                result.add(formula.right)
        elif isinstance(formula, Not):
            _collect(formula.inner)
        elif isinstance(formula, (And, Or)):
            for item in formula.items:
                _collect(item)
        elif isinstance(formula, Implies):
            _collect(formula.left)
            _collect(formula.right)

    _collect(f)
    return frozenset(result)

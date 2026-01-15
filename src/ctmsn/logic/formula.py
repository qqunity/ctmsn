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

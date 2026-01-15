from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class Predicate:
    name: str
    arity: int
    roles: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.arity <= 0:
            raise ValueError("Predicate arity must be positive")
        if self.roles and len(self.roles) != self.arity:
            raise ValueError("If roles provided, len(roles) must equal arity")

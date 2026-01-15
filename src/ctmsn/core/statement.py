from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Union

from ctmsn.core.concept import Concept

Literal = Union[str, int, float, bool]
CoreTerm = Union[Concept, Literal]


@dataclass(frozen=True)
class Statement:
    predicate: str
    args: Tuple[CoreTerm, ...]

    def __post_init__(self) -> None:
        if not self.predicate:
            raise ValueError("Statement predicate must be non-empty")
        if not self.args:
            raise ValueError("Statement must have at least 1 arg")

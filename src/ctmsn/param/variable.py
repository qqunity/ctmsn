from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from ctmsn.param.domain import Domain


@dataclass(frozen=True)
class Variable:
    name: str
    domain: Domain
    type_tag: str | None = None

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Variable name must be non-empty")

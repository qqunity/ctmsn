from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple

from ctmsn.logic.formula import Formula


@dataclass(frozen=True)
class Conditions:
    items: Tuple[Formula, ...] = ()

    def add(self, *forms: Formula) -> "Conditions":
        return Conditions(items=self.items + tuple(forms))

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Union

from ctmsn.core.concept import Concept
from ctmsn.param.variable import Variable

Literal = Union[str, int, float, bool]
Term = Union[Concept, Variable, Literal]


@dataclass(frozen=True)
class VarRef:
    var: Variable

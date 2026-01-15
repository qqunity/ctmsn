from __future__ import annotations
from enum import Enum


class TriBool(Enum):
    TRUE = "true"
    FALSE = "false"
    UNKNOWN = "unknown"

    def __bool__(self) -> bool:
        raise TypeError("TriBool cannot be coerced to bool напрямую")

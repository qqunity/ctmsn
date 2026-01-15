from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ctmsn.logic.tribool import TriBool


@dataclass
class CheckResult:
    ok: bool
    violated: list[str]
    unknown: list[str]


@dataclass
class ForceResult:
    status: TriBool
    context: Any | None
    explanation: str | None = None

from __future__ import annotations

from ctmsn.logic.formula import Formula
from ctmsn.forcing.conditions import Conditions


def invariants(*formulas: Formula) -> Conditions:
    """Собрать набор инвариантов стабилизации из формул.

    Инварианты выражаются как Conditions и проверяются ForcingEngine.check —
    отдельная логика проверки не дублируется.
    """
    return Conditions(items=tuple(formulas))

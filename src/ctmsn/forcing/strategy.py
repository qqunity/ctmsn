from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Mapping, Any

from ctmsn.param.variable import Variable
from ctmsn.param.context import Context


class Strategy:
    def candidates(self, ctx: Context, vars_to_assign: list[Variable]) -> Iterable[Mapping[Variable, Any]]:
        raise NotImplementedError


@dataclass
class BruteEnumStrategy(Strategy):
    max_branch: int = 2000

    def candidates(self, ctx: Context, vars_to_assign: list[Variable]):
        yield {}

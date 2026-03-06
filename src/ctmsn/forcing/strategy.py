from __future__ import annotations
import itertools
from dataclasses import dataclass
from typing import Iterable, Mapping, Any

from ctmsn.param.variable import Variable
from ctmsn.param.context import Context
from ctmsn.param.domain import PredicateDomain


class Strategy:
    def candidates(self, ctx: Context, vars_to_assign: list[Variable]) -> Iterable[Mapping[Variable, Any]]:
        raise NotImplementedError


@dataclass
class BruteEnumStrategy(Strategy):
    max_branch: int = 2000

    def candidates(self, ctx: Context, vars_to_assign: list[Variable]) -> Iterable[Mapping[Variable, Any]]:
        enumerable = [v for v in vars_to_assign if not isinstance(v.domain, PredicateDomain)]
        if not enumerable:
            return

        domains = [list(v.domain.enumerate_values()) for v in enumerable]

        total = 1
        for d in domains:
            total *= len(d)
            if total > self.max_branch:
                raise ValueError(f"Search space {total} exceeds max_branch={self.max_branch}")

        for combo in itertools.product(*domains):
            yield dict(zip(enumerable, combo))

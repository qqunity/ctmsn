from __future__ import annotations
from dataclasses import dataclass

from ctmsn.core.network import SemanticNetwork
from ctmsn.param.context import Context
from ctmsn.logic.formula import Formula, And
from ctmsn.logic.tribool import TriBool
from ctmsn.logic.evaluator import evaluate
from ctmsn.forcing.conditions import Conditions
from ctmsn.forcing.result import CheckResult, ForceResult
from ctmsn.forcing.strategy import Strategy, BruteEnumStrategy


@dataclass
class ForcingEngine:
    net: SemanticNetwork

    def check(self, ctx: Context, conditions: Conditions) -> CheckResult:
        violated: list[str] = []
        unknown: list[str] = []
        for i, c in enumerate(conditions.items):
            v = evaluate(c, self.net, ctx)
            if v is TriBool.FALSE:
                violated.append(f"cond[{i}]")
            elif v is TriBool.UNKNOWN:
                unknown.append(f"cond[{i}]")
        return CheckResult(ok=(not violated), violated=violated, unknown=unknown)

    def forces(self, ctx: Context, phi: Formula, conditions: Conditions) -> TriBool:
        chk = self.check(ctx, conditions)
        if not chk.ok:
            return TriBool.FALSE
        v = evaluate(phi, self.net, ctx)
        if v is TriBool.FALSE:
            return TriBool.FALSE
        if v is TriBool.TRUE and not chk.unknown:
            return TriBool.TRUE
        return TriBool.UNKNOWN

    def force(
        self,
        ctx: Context,
        phi: Formula,
        conditions: Conditions,
        strategy: Strategy | None = None,
    ) -> ForceResult:
        strategy = strategy or BruteEnumStrategy()
        cur = self.forces(ctx, phi, conditions)
        if cur is TriBool.TRUE:
            return ForceResult(status=TriBool.TRUE, context=ctx, explanation="Already forced")
        if cur is TriBool.FALSE:
            return ForceResult(status=TriBool.FALSE, context=None, explanation="Conditions or phi are false")
        return ForceResult(status=TriBool.UNKNOWN, context=None, explanation="Search not implemented yet")

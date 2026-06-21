from __future__ import annotations

from dataclasses import dataclass

from ctmsn.core.network import SemanticNetwork
from ctmsn.param.context import Context
from ctmsn.param.domain import EnumDomain
from ctmsn.param.variable import Variable


@dataclass(frozen=True)
class WorkflowVars:
    reviewer: Variable


def build_variables(net: SemanticNetwork) -> tuple[WorkflowVars, Context]:
    alice = net.concepts["alice"]
    bob = net.concepts["bob"]

    v = WorkflowVars(
        reviewer=Variable("reviewer", EnumDomain((alice, bob)), type_tag="reviewer"),
    )

    # Начальный контекст пуст: значение reviewer подбирается форсированием.
    ctx0 = Context()
    return v, ctx0

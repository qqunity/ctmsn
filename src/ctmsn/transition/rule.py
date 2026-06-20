from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Tuple, Union

from ctmsn.core.network import SemanticNetwork
from ctmsn.core.statement import Statement
from ctmsn.param.context import Context
from ctmsn.logic.formula import Formula
from ctmsn.logic.evaluator import evaluate
from ctmsn.logic.tribool import TriBool
from ctmsn.transition.event import Event


@dataclass(frozen=True)
class AddFact:
    """Декларативная операция эффекта: добавить факт."""

    predicate: str
    args: Tuple[Any, ...]


@dataclass(frozen=True)
class RetractFact:
    """Декларативная операция эффекта: убрать факт (если он присутствует)."""

    predicate: str
    args: Tuple[Any, ...]


FactOp = Union[AddFact, RetractFact]


def _resolve(net: SemanticNetwork, arg: Any) -> Any:
    """Привести строковый идентификатор концепта к Concept; иначе вернуть как есть.

    Строка, совпадающая с id зарегистрированного концепта, трактуется как
    концепт; прочие строки и значения считаются литералами (например, метки рёбер).
    """
    if isinstance(arg, str) and arg in net.concepts:
        return net.concepts[arg]
    return arg


@dataclass(frozen=True)
class TransitionRule:
    """Правило перехода: гвард (условие применимости) и декларативный эффект.

    guard — формула; правило применимо, когда она истинна (TriBool.TRUE).
    effect — последовательность операций над фактами.
    priority — чем больше, тем раньше правило рассматривается.
    on_event — если задано, правило срабатывает только на событие с этим именем.
    """

    name: str
    guard: Formula
    effect: Tuple[FactOp, ...] = ()
    priority: int = 0
    on_event: str | None = None

    def applies(
        self,
        net: SemanticNetwork,
        context: Context,
        event: Event | None = None,
    ) -> bool:
        if self.on_event is not None:
            if event is None or event.name != self.on_event:
                return False
        return evaluate(self.guard, net, context) is TriBool.TRUE

    def apply(self, net: SemanticNetwork) -> None:
        """Применить эффект к сети (мутирует переданную сеть-копию)."""
        for op in self.effect:
            resolved = tuple(_resolve(net, a) for a in op.args)
            if isinstance(op, AddFact):
                net.assert_fact(op.predicate, resolved)
            elif isinstance(op, RetractFact):
                target = Statement(predicate=op.predicate, args=resolved)
                if target in net.facts(op.predicate):
                    net.remove_fact(target)

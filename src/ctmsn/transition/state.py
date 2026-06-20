from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ctmsn.core.network import SemanticNetwork
from ctmsn.param.context import Context


class StateMode(Enum):
    """Режим состояния управляющего графа.

    TRANSIENT — переходный: существует применимое правило либо нарушены
    инварианты стабилизации.
    STABLE — устойчивый: достигнута неподвижная точка, инварианты выполнены.
    """

    TRANSIENT = "transient"
    STABLE = "stable"


@dataclass(frozen=True)
class State:
    """Снимок конфигурации: сеть, контекст параметров, номер шага и режим.

    State является неизменяемым снимком. Движок никогда не мутирует сеть уже
    созданного состояния — каждый переход порождает копию сети
    (см. SemanticNetwork.copy).
    """

    net: SemanticNetwork
    context: Context
    index: int = 0
    mode: StateMode = StateMode.TRANSIENT


def copy_context(ctx: Context) -> Context:
    """Вернуть независимую копию контекста."""
    return Context(_values=dict(ctx.as_dict()))


def make_state(net: SemanticNetwork, context: Context | None = None) -> State:
    """Построить начальное состояние из сети и (опционально) контекста.

    Сеть и контекст копируются, поэтому исходные объекты остаются неизменными.
    """
    return State(
        net=net.copy(),
        context=copy_context(context or Context()),
        index=0,
        mode=StateMode.TRANSIENT,
    )

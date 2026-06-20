"""Ограниченный model-checker переходной системы (zero-dependency).

Исчерпывающе обходит все достижимые состояния (BFS по применимым правилам,
учитывая недетерминизм порядка) и проверяет инварианты в каждом состоянии —
аналог проверки инвариантов в TLC, но без внешних инструментов. Дополняет
формальную TLA+-спецификацию (specs/Transition.tla), позволяя воспроизводить
верификацию в CI. См. docs/VERIFICATION.md.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Sequence

from ctmsn.core.network import SemanticNetwork
from ctmsn.forcing.conditions import Conditions
from ctmsn.forcing.engine import ForcingEngine
from ctmsn.param.context import Context
from ctmsn.transition.rule import TransitionRule


@dataclass(frozen=True)
class VerifyResult:
    """Итог ограниченной верификации.

    invariant_holds — выполнены ли инварианты во всех достижимых состояниях.
    counterexample — путь (имена сработавших правил) до состояния-нарушителя.
    states_explored — число обойдённых состояний.
    terminal_states — число тупиковых состояний (без применимых правил).
    truncated — был ли достигнут лимит состояний (обход неполон).
    """

    invariant_holds: bool
    states_explored: int
    counterexample: tuple[str, ...] | None
    terminal_states: int
    truncated: bool


def _state_key(net: SemanticNetwork) -> frozenset:
    return frozenset(
        (f.predicate, tuple(getattr(a, "id", a) for a in f.args)) for f in net.facts()
    )


def check_model(
    net: SemanticNetwork,
    rules: Sequence[TransitionRule],
    invariants: Conditions,
    *,
    context: Context | None = None,
    max_states: int = 10000,
) -> VerifyResult:
    """Проверить инварианты во всех достижимых состояниях переходной системы.

    Из каждого состояния применяется КАЖДОЕ применимое правило (полный обход
    недетерминизма), что строже одношагового выбора движка. Возвращает первый
    найденный контрпример (BFS — кратчайший путь).
    """
    ctx = context if context is not None else Context()
    start = net.copy()
    visited: set = {_state_key(start)}
    queue: deque = deque([(start, ())])
    explored = 0
    terminals = 0
    truncated = False

    while queue:
        cur, path = queue.popleft()
        explored += 1

        if not ForcingEngine(cur).check(ctx, invariants).ok:
            return VerifyResult(
                invariant_holds=False,
                states_explored=explored,
                counterexample=path,
                terminal_states=terminals,
                truncated=truncated,
            )

        had_successor = False
        for rule in rules:
            if not rule.applies(cur, ctx, None):
                continue
            nxt = cur.copy()
            before = _state_key(nxt)
            try:
                rule.apply(nxt)
            except ValueError:
                continue  # противоречие при применении — недопустимый переход
            key = _state_key(nxt)
            if key == before:
                continue  # неподвижная точка для этого правила
            had_successor = True
            if key in visited:
                continue
            if len(visited) >= max_states:
                truncated = True
                continue
            visited.add(key)
            queue.append((nxt, path + (rule.name,)))

        if not had_successor:
            terminals += 1

    return VerifyResult(
        invariant_holds=True,
        states_explored=explored,
        counterexample=None,
        terminal_states=terminals,
        truncated=truncated,
    )

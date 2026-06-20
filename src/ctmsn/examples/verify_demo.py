"""Демонстрация ограниченной верификации переходной системы (S5).

Проверяет денотационный инвариант во всех достижимых состояниях для двух
конфигураций: корректной (инвариант держится) и дефектной (инвариант нарушается,
выводится контрпример). Соответствует TLA+-спецификации specs/Transition.tla.

Запуск:
    python3 src/ctmsn/examples/verify_demo.py
"""

from __future__ import annotations

from ctmsn.experiment.baselines.conditions import _build_net_and_rules
from ctmsn.experiment.baselines.problem import Problem
from ctmsn.transition import check_model


def _run(label: str, problem: Problem) -> None:
    net, rules, inv = _build_net_and_rules(problem)
    res = check_model(net, rules, inv)
    print(f"[{label}] инвариант={'ДЕРЖИТСЯ' if res.invariant_holds else 'НАРУШЕН'}, "
          f"состояний={res.states_explored}, тупиков={res.terminal_states}")
    if not res.invariant_holds:
        print(f"    контрпример (путь правил): {' -> '.join(res.counterexample) or '(начальное состояние)'}")


def main() -> None:
    _run("корректная", Problem(id=0, n_stages=4, faulty=False))
    _run("дефектная", Problem(id=1, n_stages=4, faulty=True, fault_at=0))


if __name__ == "__main__":
    main()

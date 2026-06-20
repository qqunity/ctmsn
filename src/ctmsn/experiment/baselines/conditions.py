from __future__ import annotations

import time
from dataclasses import dataclass

from ctmsn.core.concept import Concept
from ctmsn.core.network import SemanticNetwork
from ctmsn.core.predicate import Predicate
from ctmsn.forcing.conditions import Conditions
from ctmsn.logic.formula import FactAtom, Or
from ctmsn.transition.engine import TransitionEngine, make_state
from ctmsn.transition.invariant import invariants
from ctmsn.transition.rule import AddFact, FactOp, RetractFact, TransitionRule
from ctmsn.experiment.baselines.problem import Problem


@dataclass(frozen=True)
class ConditionOutcome:
    """Результат одного условия на одном экземпляре задачи.

    detected — обнаружил ли подход нарушение во время прогона.
    final_consistent — согласовано ли итоговое состояние при пост-аудите
    (объект ровно на одной стадии).
    undetected_inconsistency — 1, если итог несогласован и нарушение не было
    обнаружено (молчаливая ошибка); ключевая метрика для H1/H4.
    """

    condition: str
    problem_id: int
    faulty: bool
    detected: bool
    final_consistent: bool
    undetected_inconsistency: int
    steps: int
    duration_ms: float


def _build_net_and_rules(problem: Problem):
    net = SemanticNetwork()
    stages = problem.stages()
    net.add_concept(Concept(id="obj", label="Объект"))
    for s in stages:
        net.add_concept(Concept(id=s, label=s.upper()))
    net.add_predicate(Predicate(name="at", arity=2))
    net.assert_fact("at", (net.concepts["obj"], net.concepts[stages[0]]))

    obj = net.concepts["obj"]
    rules: list[TransitionRule] = []
    for i in range(problem.n_stages - 1):
        src, dst = stages[i], stages[i + 1]
        effect: list[FactOp] = [RetractFact("at", ("obj", src))]
        if not (problem.faulty and i == problem.fault_at):
            effect.append(AddFact("at", ("obj", dst)))
        rules.append(
            TransitionRule(
                name=f"{src}->{dst}",
                guard=FactAtom("at", (obj, net.concepts[src])),
                effect=tuple(effect),
            )
        )
    invariant = invariants(
        Or(tuple(FactAtom("at", (obj, net.concepts[s])) for s in stages))
    )
    return net, rules, invariant


def _audit_consistent(net: SemanticNetwork) -> bool:
    """Объект согласован тогда и только тогда, когда находится ровно на одной стадии."""
    at_facts = [f for f in net.facts("at") if getattr(f.args[0], "id", None) == "obj"]
    return len(at_facts) == 1


def run_candidate(problem: Problem) -> ConditionOutcome:
    """Условие C: композиционная модель с денотационным/инвариантным слоем."""
    net, rules, inv = _build_net_and_rules(problem)
    engine = TransitionEngine(rules=rules, invariants=inv, max_steps=100)
    t0 = time.perf_counter()
    state = make_state(net)
    trace = engine.run_to_fixpoint(state)
    # Воспроизвести шаги для аудита итогового состояния.
    cur = make_state(net)
    for _ in range(len(trace.steps)):
        res = engine.step(cur, None)
        if res is None:
            break
        cur, _ = res
    dt = (time.perf_counter() - t0) * 1000.0
    detected = any(not s.invariants_ok for s in trace.steps)
    consistent = _audit_consistent(cur.net)
    undetected = 1 if (not consistent and not detected) else 0
    return ConditionOutcome(
        condition="C", problem_id=problem.id, faulty=problem.faulty,
        detected=detected, final_consistent=consistent,
        undetected_inconsistency=undetected, steps=len(trace.steps),
        duration_ms=round(dt, 3),
    )


def run_graph_baseline(problem: Problem) -> ConditionOutcome:
    """Условие B: тот же граф переходов, но БЕЗ денотационного слоя (нет инвариантов)."""
    net, rules, _inv = _build_net_and_rules(problem)
    engine = TransitionEngine(rules=rules, invariants=Conditions(), max_steps=100)
    t0 = time.perf_counter()
    state = make_state(net)
    trace = engine.run_to_fixpoint(state)
    cur = make_state(net)
    for _ in range(len(trace.steps)):
        res = engine.step(cur, None)
        if res is None:
            break
        cur, _ = res
    dt = (time.perf_counter() - t0) * 1000.0
    detected = any(not s.invariants_ok for s in trace.steps)  # всегда False: инвариантов нет
    consistent = _audit_consistent(cur.net)
    undetected = 1 if (not consistent and not detected) else 0
    return ConditionOutcome(
        condition="B", problem_id=problem.id, faulty=problem.faulty,
        detected=detected, final_consistent=consistent,
        undetected_inconsistency=undetected, steps=len(trace.steps),
        duration_ms=round(dt, 3),
    )


def run_imperative(problem: Problem) -> ConditionOutcome:
    """Условие A: ручная императивная симуляция на dict, без графа и проверок."""
    stages = problem.stages()
    trans: dict[str, str | None] = {}
    for i in range(problem.n_stages - 1):
        dst = None if (problem.faulty and i == problem.fault_at) else stages[i + 1]
        trans[stages[i]] = dst

    t0 = time.perf_counter()
    state: str | None = stages[0]
    steps = 0
    while state in trans and steps < 100:
        state = trans[state]
        steps += 1
        if state is None:
            break
    dt = (time.perf_counter() - t0) * 1000.0
    consistent = state is not None
    detected = False  # императивный код не проверяет согласованность
    undetected = 1 if (not consistent and not detected) else 0
    return ConditionOutcome(
        condition="A", problem_id=problem.id, faulty=problem.faulty,
        detected=detected, final_consistent=consistent,
        undetected_inconsistency=undetected, steps=steps,
        duration_ms=round(dt, 3),
    )


CONDITIONS = {
    "A": run_imperative,
    "B": run_graph_baseline,
    "C": run_candidate,
}


def run_all_conditions(problems) -> dict[str, list[ConditionOutcome]]:
    """Прогнать все условия на наборе задач. Возвращает {condition: [outcomes]}."""
    out: dict[str, list[ConditionOutcome]] = {k: [] for k in CONDITIONS}
    for p in problems:
        for key, fn in CONDITIONS.items():
            out[key].append(fn(p))
    return out

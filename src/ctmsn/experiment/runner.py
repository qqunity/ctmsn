from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Sequence

from ctmsn.transition.engine import TransitionEngine, make_state
from ctmsn.transition.trace import Trace
from ctmsn.experiment.case import ExperimentCase
from ctmsn.experiment.metrics import RunMetrics, compute_metrics


@dataclass(frozen=True)
class RunResult:
    case: str
    trace: Trace
    metrics: RunMetrics


def run_case(case: ExperimentCase, repeats: int = 1) -> RunResult:
    """Прогнать один кейс до неподвижной точки и собрать метрики.

    repeats > 1 повторяет прогон и берёт наименьшую длительность как наиболее
    устойчивую оценку (результат переходов детерминирован, варьируется лишь время).
    """
    engine = TransitionEngine(
        rules=list(case.rules),
        invariants=case.invariants,
        max_steps=case.max_steps,
    )
    best_ms: float | None = None
    trace: Trace | None = None
    for _ in range(max(1, repeats)):
        state = make_state(case.net, case.context)
        t0 = time.perf_counter()
        trace = engine.run_to_fixpoint(state)
        dt = (time.perf_counter() - t0) * 1000.0
        best_ms = dt if best_ms is None else min(best_ms, dt)

    assert trace is not None
    metrics = compute_metrics(case.name, trace, best_ms or 0.0)
    return RunResult(case=case.name, trace=trace, metrics=metrics)


def run_suite(cases: Sequence[ExperimentCase], repeats: int = 1) -> list[RunResult]:
    """Прогнать набор кейсов и вернуть результаты в порядке следования."""
    return [run_case(c, repeats=repeats) for c in cases]

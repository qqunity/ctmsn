from __future__ import annotations

from dataclasses import dataclass

from ctmsn.transition.state import StateMode
from ctmsn.transition.trace import Trace


@dataclass(frozen=True)
class RunMetrics:
    """Метрики одного прогона, вычисленные из трассы переходов.

    convergence_steps — число шагов до устойчивого режима (Convergence Time);
    None, если устойчивость не достигнута.
    constraint_satisfaction_rate — доля шагов с выполненными инвариантами
    (Constraint Satisfaction Rate); 1.0, если переходов не было.
    """

    case: str
    final_mode: str
    converged: bool
    convergence_steps: int | None
    total_steps: int
    constraint_satisfaction_rate: float
    invariant_violations: int
    rules_fired: int
    distinct_rules_fired: int
    duration_ms: float


def compute_metrics(case: str, trace: Trace, duration_ms: float) -> RunMetrics:
    steps = trace.steps
    total = len(steps)
    violations = sum(1 for s in steps if not s.invariants_ok)
    csr = 1.0 if total == 0 else round((total - violations) / total, 4)
    distinct = len({s.rule for s in steps})
    return RunMetrics(
        case=case,
        final_mode=trace.final_mode.value,
        converged=trace.final_mode is StateMode.STABLE,
        convergence_steps=trace.convergence_steps,
        total_steps=total,
        constraint_satisfaction_rate=csr,
        invariant_violations=violations,
        rules_fired=total,
        distinct_rules_fired=distinct,
        duration_ms=round(duration_ms, 3),
    )

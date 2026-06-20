"""Сводка и статистическое сравнение условий A/B/C.

Импорт статистики (scipy) выполняется лениво внутри функций, поэтому модуль
можно импортировать без extras; статистика нужна лишь для compare_pair.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ctmsn.experiment.baselines.conditions import ConditionOutcome


@dataclass(frozen=True)
class ConditionSummary:
    condition: str
    n: int
    n_faulty: int
    detection_rate_on_faulty: float
    final_consistency_rate: float
    mean_undetected: float
    total_undetected: int


def summarize(condition: str, outcomes: Sequence[ConditionOutcome]) -> ConditionSummary:
    n = len(outcomes)
    faulty = [o for o in outcomes if o.faulty]
    detected_faulty = sum(1 for o in faulty if o.detected)
    consistent = sum(1 for o in outcomes if o.final_consistent)
    undetected = [o.undetected_inconsistency for o in outcomes]
    return ConditionSummary(
        condition=condition,
        n=n,
        n_faulty=len(faulty),
        detection_rate_on_faulty=round(detected_faulty / len(faulty), 4) if faulty else 1.0,
        final_consistency_rate=round(consistent / n, 4) if n else 1.0,
        mean_undetected=round(sum(undetected) / n, 4) if n else 0.0,
        total_undetected=sum(undetected),
    )


@dataclass(frozen=True)
class PairwiseComparison:
    metric: str
    candidate: str
    baseline: str
    mann_whitney: object  # MannWhitneyResult
    bootstrap: object  # BootstrapCI


def compare_pair(
    results: dict[str, list[ConditionOutcome]],
    candidate: str = "C",
    baseline: str = "B",
    metric: str = "undetected_inconsistency",
    seed: int = 0,
) -> PairwiseComparison:
    """Сравнить candidate vs baseline по метрике (Mann–Whitney + bootstrap CI)."""
    from ctmsn.experiment.stats import mann_whitney_u, bootstrap_ci_diff

    cand = [getattr(o, metric) for o in results[candidate]]
    base = [getattr(o, metric) for o in results[baseline]]
    mw = mann_whitney_u(base, cand, alternative="greater")  # baseline > candidate?
    boot = bootstrap_ci_diff(base, cand, statistic="mean", seed=seed)
    return PairwiseComparison(
        metric=metric, candidate=candidate, baseline=baseline,
        mann_whitney=mw, bootstrap=boot,
    )


def format_summaries(summaries: Sequence[ConditionSummary]) -> str:
    cols = [
        ("condition", "усл.", 5),
        ("n", "N", 5),
        ("n_faulty", "деф.", 5),
        ("detection_rate_on_faulty", "детект", 7),
        ("final_consistency_rate", "консист", 8),
        ("mean_undetected", "ср.незам", 9),
        ("total_undetected", "всего", 6),
    ]
    head = " | ".join(t.ljust(w) for _, t, w in cols)
    lines = [head, "-" * len(head)]
    for s in summaries:
        d = s.__dict__
        lines.append(" | ".join(str(d[k]).ljust(w) for k, _, w in cols))
    return "\n".join(lines)

from __future__ import annotations

import csv
import json
from dataclasses import asdict, fields
from typing import Sequence

from ctmsn.experiment.metrics import RunMetrics
from ctmsn.experiment.runner import RunResult

_METRIC_FIELDS = [f.name for f in fields(RunMetrics)]


def results_to_dicts(results: Sequence[RunResult]) -> list[dict]:
    return [asdict(r.metrics) for r in results]


def write_json(path: str, results: Sequence[RunResult]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results_to_dicts(results), f, ensure_ascii=False, indent=2)


def write_csv(path: str, results: Sequence[RunResult]) -> None:
    rows = results_to_dicts(results)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=_METRIC_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def format_table(results: Sequence[RunResult]) -> str:
    """Текстовая таблица метрик для вывода в консоль/протокол."""
    cols = [
        ("case", "кейс", 16),
        ("final_mode", "режим", 10),
        ("convergence_steps", "сходимость", 11),
        ("total_steps", "шагов", 6),
        ("constraint_satisfaction_rate", "CSR", 6),
        ("invariant_violations", "наруш.", 7),
        ("duration_ms", "мс", 8),
    ]
    rows = results_to_dicts(results)
    head = " | ".join(title.ljust(w) for _, title, w in cols)
    sep = "-" * len(head)
    lines = [head, sep]
    for row in rows:
        cells = []
        for key, _, w in cols:
            val = row.get(key)
            cells.append(("—" if val is None else str(val)).ljust(w))
        lines.append(" | ".join(cells))
    return "\n".join(lines)

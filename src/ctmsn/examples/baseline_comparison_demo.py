"""Сравнение условий A/B/C с проверкой гипотез (S3).

Условия:
  A — императивная модель (dict, без графа и проверок),
  B — графовая модель переходов БЕЗ денотационного слоя (нет инвариантов),
  C — композиционная модель с денотационным/инвариантным слоем (CTMSN).

Метрика — undetected_inconsistency: молчаливые семантические несогласованности.
Гипотеза H1/H4: C обнаруживает нарушения, которые A и B пропускают.

Запуск (требует extras: pip install -e '.[experiment]'):
    python3 src/ctmsn/examples/baseline_comparison_demo.py
"""

from __future__ import annotations

import argparse

from ctmsn.experiment.baselines import generate_problems, run_all_conditions
from ctmsn.experiment.compare import compare_pair, format_summaries, summarize


def main() -> None:
    parser = argparse.ArgumentParser(description="Сравнение baseline A/B/C")
    parser.add_argument("--count", type=int, default=40)
    parser.add_argument("--fault-ratio", type=float, default=0.5)
    parser.add_argument("--stages", type=int, default=4)
    args = parser.parse_args()

    problems = generate_problems(
        args.count, fault_ratio=args.fault_ratio, n_stages=args.stages
    )
    results = run_all_conditions(problems)

    summaries = [summarize(k, results[k]) for k in ("A", "B", "C")]
    print(format_summaries(summaries))

    print("\nСтатистическое сравнение (метрика: незамеченные несогласованности)")
    for base in ("A", "B"):
        cmp = compare_pair(results, candidate="C", baseline=base)
        mw = cmp.mann_whitney
        ci = cmp.bootstrap
        print(
            f"  {base} vs C: U={mw.u:.1f}, p={mw.p_value:.4g}; "
            f"разность средних ({base}−C)={ci.point} "
            f"CI{int(ci.confidence*100)}%=[{ci.low}, {ci.high}] ({ci.method})"
        )


if __name__ == "__main__":
    main()

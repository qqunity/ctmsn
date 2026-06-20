"""Демонстрация экспериментального контура (S2).

Прогоняет набор кейсов ступенчатого процесса с разными свойствами
(сходящийся, более длинный, циклический, с нарушением инварианта),
печатает таблицу метрик и экспортирует артефакты JSON/CSV.

Запуск:
    python3 src/ctmsn/examples/experiment_demo.py [--out DIR] [--repeats N]
"""

from __future__ import annotations

import argparse
import os

from ctmsn.experiment import (
    format_table,
    run_suite,
    staged_process_case,
    write_csv,
    write_json,
)


def build_suite():
    return [
        staged_process_case("staged-3", 3),
        staged_process_case("staged-5", 5),
        staged_process_case("cyclic", 3, cyclic=True),
        staged_process_case("leaky", 3, leaky=True),
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Экспериментальный контур CTMSN")
    parser.add_argument("--out", default=None, help="каталог для артефактов JSON/CSV")
    parser.add_argument("--repeats", type=int, default=3, help="повторов для оценки времени")
    args = parser.parse_args()

    results = run_suite(build_suite(), repeats=args.repeats)
    print(format_table(results))

    if args.out:
        os.makedirs(args.out, exist_ok=True)
        json_path = os.path.join(args.out, "experiment.json")
        csv_path = os.path.join(args.out, "experiment.csv")
        write_json(json_path, results)
        write_csv(csv_path, results)
        print(f"\nАртефакты: {json_path}, {csv_path}")


if __name__ == "__main__":
    main()

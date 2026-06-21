"""Витринный сценарий «Документооборот»: все доработки роадмапа в одном потоке.

Демонстрирует на одном сценарии: форсинг (S0/S?), переходные/устойчивые режимы (S1),
экспериментальные метрики (S2), формальную верификацию (S5), декларативный DSL (S4).

Запуск:
    python3 src/ctmsn/examples/doc_workflow_demo.py
"""

from __future__ import annotations

from ctmsn.scenarios.doc_workflow.runner import run


def main() -> None:
    out = run()

    print("== Форсинг до переходов (документ — черновик) ==")
    print(f"  check:  {out['before']['check']}")
    print(f"  forces: {out['before']['forces']}")
    print(f"  force:  {out['before']['force'].status}")

    print("\n== Переходы (S1) ==")
    print(out["trace"])

    print("\n== Форсинг после переходов (документ опубликован) ==")
    print(f"  forces: {out['after']['forces']}")
    fr = out["after"]["force"]
    print(f"  force:  {fr.status} — {fr.explanation}")

    print("\n== Верификация (S5) ==")
    v = out["verification"]
    print(f"  инвариант={'ДЕРЖИТСЯ' if v.invariant_holds else 'НАРУШЕН'}, "
          f"состояний={v.states_explored}, тупиков={v.terminal_states}")

    print("\n== Метрики (S2) ==")
    m = out["metrics"]
    print(f"  режим={m.final_mode}, сходимость={m.convergence_steps}, "
          f"CSR={m.constraint_satisfaction_rate}, шагов={m.total_steps}")

    print("\n== DSL round-trip (S4) ==")
    print(f"  поведение сохранено: {out['dsl_roundtrip_ok']}")


if __name__ == "__main__":
    main()

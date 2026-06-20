"""Демонстрация декларативного описания модели (S4).

Модель (сеть + правила переходов + инварианты) описывается одним JSON/YAML
документом, загружается и исполняется движком переходов. Показан round-trip
(load -> dump -> load) и, при наличии pyyaml, сериализация в YAML.

Запуск:
    python3 src/ctmsn/examples/dsl_demo.py
"""

from __future__ import annotations


from ctmsn.io import dumps_model_json, load_model, loads_model_json


def _fact(pred, *ids):
    return {"type": "FactAtom", "predicate": pred,
            "args": [{"kind": "concept", "id": i} for i in ids]}


MODEL_DOC = {
    "concepts": {
        "obj": {"id": "obj", "label": "Объект", "tags": [], "meta": {}},
        "a": {"id": "a", "label": "A", "tags": [], "meta": {}},
        "b": {"id": "b", "label": "B", "tags": [], "meta": {}},
        "c": {"id": "c", "label": "C", "tags": [], "meta": {}},
    },
    "predicates": {"at": {"name": "at", "arity": 2, "roles": []}},
    "facts": [{"predicate": "at", "args": ["obj", "a"]}],
    "transitions": {
        "rules": [
            {"name": "A->B", "guard": _fact("at", "obj", "a"),
             "effect": [{"op": "retract", "predicate": "at", "args": ["obj", "a"]},
                        {"op": "add", "predicate": "at", "args": ["obj", "b"]}],
             "priority": 0, "on_event": None},
            {"name": "B->C", "guard": _fact("at", "obj", "b"),
             "effect": [{"op": "retract", "predicate": "at", "args": ["obj", "b"]},
                        {"op": "add", "predicate": "at", "args": ["obj", "c"]}],
             "priority": 0, "on_event": None},
        ],
        "invariants": [
            {"type": "Or", "items": [_fact("at", "obj", "a"),
                                     _fact("at", "obj", "b"),
                                     _fact("at", "obj", "c")]}
        ],
    },
}


def main() -> None:
    model = load_model(MODEL_DOC)
    print(f"Загружено: концептов={len(model.network.concepts)}, "
          f"правил={len(model.rules)}, инвариантов={len(model.invariants.items)}")

    trace = model.engine().run_to_fixpoint(model.initial_state())
    print(trace)

    # Round-trip через JSON
    restored = loads_model_json(dumps_model_json(model))
    trace2 = restored.engine().run_to_fixpoint(restored.initial_state())
    same = trace2.final_mode == trace.final_mode and trace2.convergence_steps == trace.convergence_steps
    print(f"\nRound-trip JSON: итог совпадает = {same}")

    try:
        from ctmsn.io import dumps_model_yaml
        print("\nYAML-представление (фрагмент):")
        print("\n".join(dumps_model_yaml(model).splitlines()[:6]))
    except ImportError:
        print("\n(pyyaml не установлен — YAML пропущен; pip install -e '.[io]')")


if __name__ == "__main__":
    main()

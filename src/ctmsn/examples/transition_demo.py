"""Демонстрация переходных и устойчивых режимов.

Моделируется ступенчатый процесс: объект последовательно проходит стадии
A -> B -> C. Каждая стадия — переходный режим (есть применимое правило);
по достижении стадии C применимых правил больше нет и инварианты выполнены —
это устойчивый режим.

Запуск:
    python3 src/ctmsn/examples/transition_demo.py
"""

from __future__ import annotations

from ctmsn.core.concept import Concept
from ctmsn.core.network import SemanticNetwork
from ctmsn.core.predicate import Predicate
from ctmsn.logic.formula import FactAtom, Or
from ctmsn.transition import (
    AddFact,
    RetractFact,
    TransitionEngine,
    TransitionRule,
    invariants,
    make_state,
)


def build_network() -> SemanticNetwork:
    net = SemanticNetwork()
    obj = Concept(id="obj", label="Объект")
    a = Concept(id="a", label="Стадия A")
    b = Concept(id="b", label="Стадия B")
    c = Concept(id="c", label="Стадия C")
    for concept in (obj, a, b, c):
        net.add_concept(concept)
    net.add_predicate(Predicate(name="at", arity=2))
    net.assert_fact("at", (obj, a))
    return net


def build_rules(net: SemanticNetwork) -> list[TransitionRule]:
    obj, a, b, c = (net.concepts[i] for i in ("obj", "a", "b", "c"))
    return [
        TransitionRule(
            name="A->B",
            guard=FactAtom("at", (obj, a)),
            effect=(RetractFact("at", ("obj", "a")), AddFact("at", ("obj", "b"))),
        ),
        TransitionRule(
            name="B->C",
            guard=FactAtom("at", (obj, b)),
            effect=(RetractFact("at", ("obj", "b")), AddFact("at", ("obj", "c"))),
        ),
    ]


def build_invariants(net: SemanticNetwork):
    obj, a, b, c = (net.concepts[i] for i in ("obj", "a", "b", "c"))
    # Безопасность: объект всегда находится ровно на одной из известных стадий.
    return invariants(
        Or((FactAtom("at", (obj, a)), FactAtom("at", (obj, b)), FactAtom("at", (obj, c))))
    )


def main() -> None:
    net = build_network()
    engine = TransitionEngine(
        rules=build_rules(net),
        invariants=build_invariants(net),
        max_steps=50,
    )
    trace = engine.run_to_fixpoint(make_state(net))
    print(trace)


if __name__ == "__main__":
    main()

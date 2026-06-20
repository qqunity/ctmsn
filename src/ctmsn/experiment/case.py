from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from ctmsn.core.concept import Concept
from ctmsn.core.network import SemanticNetwork
from ctmsn.core.predicate import Predicate
from ctmsn.forcing.conditions import Conditions
from ctmsn.logic.formula import FactAtom, Or
from ctmsn.param.context import Context
from ctmsn.transition.invariant import invariants
from ctmsn.transition.rule import AddFact, FactOp, RetractFact, TransitionRule


@dataclass(frozen=True)
class ExperimentCase:
    """Конфигурация эксперимента: сеть, правила, инварианты и параметры прогона.

    Сеть и контекст копируются движком на каждом прогоне (snapshot-семантика),
    поэтому один и тот же кейс можно прогонять многократно без побочных эффектов.
    """

    name: str
    net: SemanticNetwork
    rules: Sequence[TransitionRule]
    invariants: Conditions = field(default_factory=Conditions)
    context: Context | None = None
    max_steps: int = 100


def staged_process_case(
    name: str,
    n_stages: int,
    *,
    cyclic: bool = False,
    leaky: bool = False,
    with_invariant: bool = True,
) -> ExperimentCase:
    """Построить кейс ступенчатого процесса obj: s0 -> s1 -> ... -> s{n-1}.

    cyclic — последняя стадия возвращает объект на первую (нет сходимости).
    leaky — первое правило не добавляет следующую стадию (нарушение инварианта).
    """
    if n_stages < 2:
        raise ValueError("n_stages must be >= 2")

    net = SemanticNetwork()
    stages = [f"s{i}" for i in range(n_stages)]
    net.add_concept(Concept(id="obj", label="Объект"))
    for s in stages:
        net.add_concept(Concept(id=s, label=s.upper()))
    net.add_predicate(Predicate(name="at", arity=2))
    net.assert_fact("at", (net.concepts["obj"], net.concepts[stages[0]]))

    obj = net.concepts["obj"]
    rules: list[TransitionRule] = []
    for i in range(n_stages - 1):
        src, dst = stages[i], stages[i + 1]
        effect: list[FactOp] = [RetractFact("at", ("obj", src))]
        if not (leaky and i == 0):
            effect.append(AddFact("at", ("obj", dst)))
        rules.append(
            TransitionRule(
                name=f"{src}->{dst}",
                guard=FactAtom("at", (obj, net.concepts[src])),
                effect=tuple(effect),
            )
        )
    if cyclic:
        last, first = stages[-1], stages[0]
        rules.append(
            TransitionRule(
                name=f"{last}->{first}",
                guard=FactAtom("at", (obj, net.concepts[last])),
                effect=(RetractFact("at", ("obj", last)), AddFact("at", ("obj", first))),
            )
        )

    conds: Conditions = Conditions()
    if with_invariant:
        conds = invariants(
            Or(tuple(FactAtom("at", (obj, net.concepts[s])) for s in stages))
        )

    return ExperimentCase(name=name, net=net, rules=rules, invariants=conds)

from __future__ import annotations

from ctmsn.core.concept import Concept
from ctmsn.core.predicate import Predicate
from ctmsn.core.network import SemanticNetwork
from ctmsn.core.statement import Statement
from ctmsn.logic.formula import FactAtom, Or
from ctmsn.transition import (
    AddFact,
    RetractFact,
    StateMode,
    TransitionEngine,
    TransitionRule,
    invariants,
    make_state,
)


def _stage_network(start: str = "a") -> SemanticNetwork:
    net = SemanticNetwork()
    for cid, label in (("obj", "Объект"), ("a", "A"), ("b", "B"), ("c", "C")):
        net.add_concept(Concept(id=cid, label=label))
    net.add_predicate(Predicate(name="at", arity=2))
    net.assert_fact("at", (net.concepts["obj"], net.concepts[start]))
    return net


def _ab_bc_rules(net: SemanticNetwork) -> list[TransitionRule]:
    obj, a, b = net.concepts["obj"], net.concepts["a"], net.concepts["b"]
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


def _stage_invariant(net: SemanticNetwork):
    obj, a, b, c = (net.concepts[i] for i in ("obj", "a", "b", "c"))
    return invariants(
        Or((FactAtom("at", (obj, a)), FactAtom("at", (obj, b)), FactAtom("at", (obj, c))))
    )


class TestTransitionEngine:
    def test_single_step(self):
        net = _stage_network("a")
        engine = TransitionEngine(rules=_ab_bc_rules(net))
        result = engine.step(make_state(net))
        assert result is not None
        new_state, step = result
        assert step.rule == "A->B"
        assert new_state.index == 1
        assert step.added == ("at(obj, b)",)
        assert step.removed == ("at(obj, a)",)
        # Объект теперь на стадии B.
        facts = {(s.predicate, tuple(a.id for a in s.args)) for s in new_state.net.facts("at")}
        assert ("at", ("obj", "b")) in facts

    def test_converges_to_stable(self):
        net = _stage_network("a")
        engine = TransitionEngine(
            rules=_ab_bc_rules(net), invariants=_stage_invariant(net)
        )
        trace = engine.run_to_fixpoint(make_state(net))
        assert trace.final_mode is StateMode.STABLE
        assert trace.convergence_steps == 2
        assert len(trace.steps) == 2
        assert all(s.invariants_ok for s in trace.steps)
        assert trace.steps[-1].mode is StateMode.STABLE

    def test_invariant_violation_keeps_transient(self):
        net = _stage_network("a")
        leak = TransitionRule(
            name="leak",
            guard=FactAtom("at", (net.concepts["obj"], net.concepts["a"])),
            effect=(RetractFact("at", ("obj", "a")),),  # объект исчезает
        )
        engine = TransitionEngine(rules=[leak], invariants=_stage_invariant(net))
        trace = engine.run_to_fixpoint(make_state(net))
        assert trace.final_mode is StateMode.TRANSIENT
        assert trace.convergence_steps is None
        assert trace.steps[-1].invariants_ok is False
        assert trace.steps[-1].mode is StateMode.TRANSIENT

    def test_dead_end_on_step_limit(self):
        net = _stage_network("a")
        obj, a, b = net.concepts["obj"], net.concepts["a"], net.concepts["b"]
        cycle = [
            TransitionRule(
                name="A->B",
                guard=FactAtom("at", (obj, a)),
                effect=(RetractFact("at", ("obj", "a")), AddFact("at", ("obj", "b"))),
            ),
            TransitionRule(
                name="B->A",
                guard=FactAtom("at", (obj, b)),
                effect=(RetractFact("at", ("obj", "b")), AddFact("at", ("obj", "a"))),
            ),
        ]
        engine = TransitionEngine(rules=cycle, max_steps=5)
        trace = engine.run_to_fixpoint(make_state(net))
        assert trace.final_mode is StateMode.TRANSIENT
        assert trace.convergence_steps is None
        assert len(trace.steps) == 5

    def test_idempotent_when_already_stable(self):
        net = _stage_network("c")  # уже на финальной стадии
        engine = TransitionEngine(
            rules=_ab_bc_rules(net), invariants=_stage_invariant(net)
        )
        state = make_state(net)
        assert engine.step(state) is None
        trace = engine.run_to_fixpoint(state)
        assert trace.final_mode is StateMode.STABLE
        assert trace.convergence_steps == 0
        assert trace.steps == ()

    def test_original_network_unchanged(self):
        net = _stage_network("a")
        engine = TransitionEngine(rules=_ab_bc_rules(net))
        engine.run_to_fixpoint(make_state(net))
        # Исходная сеть не мутирована движком (snapshot-семантика).
        at_facts = {(s.predicate, tuple(a.id for a in s.args)) for s in net.facts("at")}
        assert at_facts == {("at", ("obj", "a"))}

    def test_event_driven_step(self):
        net = _stage_network("a")
        obj, a, b = net.concepts["obj"], net.concepts["a"], net.concepts["b"]
        rule = TransitionRule(
            name="advance",
            guard=FactAtom("at", (obj, a)),
            effect=(RetractFact("at", ("obj", "a")), AddFact("at", ("obj", "b"))),
            on_event="advance",
        )
        engine = TransitionEngine(rules=[rule])
        state = make_state(net)
        # Без события правило не применяется.
        assert engine.step(state, None) is None
        from ctmsn.transition import Event

        result = engine.step(state, Event(name="advance"))
        assert result is not None
        _, step = result
        assert step.rule == "advance"
        assert step.event == "advance"

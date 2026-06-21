from __future__ import annotations

from ctmsn.logic.tribool import TriBool
from ctmsn.transition import TransitionEngine, check_model, make_state
from ctmsn.transition.event import Event

from ctmsn.scenarios.doc_workflow.model import build_network
from ctmsn.scenarios.doc_workflow.transition import build_invariants, build_rules
from ctmsn.scenarios.doc_workflow.runner import run


class TestDocWorkflowBuild:
    def test_network_builds(self):
        net = build_network()
        assert "doc" in net.concepts
        assert "status" in net.predicates
        status_facts = list(net.facts("status"))
        assert len(status_facts) == 1  # документ ровно в одном статусе


class TestDocWorkflowTransitions:
    def test_converges_to_published(self):
        net = build_network()
        engine = TransitionEngine(rules=build_rules(net), invariants=build_invariants(net))
        trace = engine.run_to_fixpoint(make_state(net))
        assert trace.final_mode.value == "stable"
        assert trace.convergence_steps == 3
        assert [s.rule for s in trace.steps] == ["submit", "approve", "publish"]
        assert all(s.invariants_ok for s in trace.steps)

    def test_reject_is_event_gated(self):
        net = build_network()
        rules = build_rules(net)
        # Перевести документ в review (submit), затем reject — только по событию.
        engine = TransitionEngine(rules=rules, invariants=build_invariants(net))
        s0 = make_state(net)
        s1, _ = engine.step(s0, None)  # submit -> review
        # Без события автономный шаг выберет approve, не reject.
        s2, rec = engine.step(s1, None)
        assert rec.rule == "approve"
        # С событием reject из review возвращаемся в draft.
        res = engine.step(s1, Event(name="reject"))
        assert res is not None
        _, rrec = res
        assert rrec.rule == "reject"


class TestDocWorkflowVerification:
    def test_invariant_holds_over_reachable_states(self):
        net = build_network()
        res = check_model(net, build_rules(net), build_invariants(net))
        assert res.invariant_holds is True
        assert res.counterexample is None
        assert res.truncated is False


class TestDocWorkflowPipeline:
    def test_full_run(self):
        out = run()
        # Цель недостижима до переходов, достижима после (reviewer подобран).
        assert out["before"]["forces"] is TriBool.FALSE
        assert out["after"]["force"].status is TriBool.TRUE
        # Форсирование подобрало рецензента alice
        assert out["after"]["force"].context.as_dict()["reviewer"].id == "alice"
        # Переходы и метрики
        assert out["trace"].final_mode.value == "stable"
        assert out["metrics"].convergence_steps == 3
        assert out["metrics"].constraint_satisfaction_rate == 1.0
        # Верификация и DSL
        assert out["verification"].invariant_holds is True
        assert out["dsl_roundtrip_ok"] is True

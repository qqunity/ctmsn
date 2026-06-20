from __future__ import annotations

from ctmsn.experiment.baselines.conditions import _build_net_and_rules
from ctmsn.experiment.baselines.problem import Problem
from ctmsn.transition import check_model


class TestModelChecker:
    def test_consistent_model_invariant_holds(self):
        net, rules, inv = _build_net_and_rules(Problem(id=0, n_stages=4, faulty=False))
        res = check_model(net, rules, inv)
        assert res.invariant_holds is True
        assert res.counterexample is None
        assert res.states_explored >= 4  # s0..s3
        assert res.terminal_states >= 1
        assert res.truncated is False

    def test_faulty_model_invariant_violated_with_counterexample(self):
        net, rules, inv = _build_net_and_rules(Problem(id=1, n_stages=4, faulty=True, fault_at=0))
        res = check_model(net, rules, inv)
        assert res.invariant_holds is False
        assert res.counterexample is not None
        # дефект на первом переходе s0->s1
        assert res.counterexample[0] == "s0->s1"

    def test_fault_at_later_stage_still_detected(self):
        net, rules, inv = _build_net_and_rules(Problem(id=2, n_stages=5, faulty=True, fault_at=2))
        res = check_model(net, rules, inv)
        assert res.invariant_holds is False
        assert res.counterexample is not None
        assert "s2->s3" in res.counterexample

    def test_max_states_truncation_flag(self):
        net, rules, inv = _build_net_and_rules(Problem(id=3, n_stages=6, faulty=False))
        res = check_model(net, rules, inv, max_states=2)
        # При очень малом лимите обход неполон, но безопасность на достигнутых ок
        assert res.invariant_holds is True
        assert res.truncated is True

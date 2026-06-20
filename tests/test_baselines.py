from __future__ import annotations

from ctmsn.experiment.baselines import (
    Problem,
    generate_problems,
    run_all_conditions,
    run_candidate,
    run_graph_baseline,
    run_imperative,
)
from ctmsn.experiment.compare import summarize


class TestBaselineConditions:
    def test_clean_problem_all_consistent(self):
        p = Problem(id=0, n_stages=4, faulty=False)
        for fn in (run_candidate, run_graph_baseline, run_imperative):
            o = fn(p)
            assert o.final_consistent is True
            assert o.undetected_inconsistency == 0
            assert o.detected is False

    def test_faulty_problem_candidate_detects(self):
        p = Problem(id=1, n_stages=4, faulty=True, fault_at=1)
        c = run_candidate(p)
        assert c.detected is True              # инвариант поймал нарушение
        assert c.undetected_inconsistency == 0  # не молчаливое

    def test_faulty_problem_baselines_miss(self):
        p = Problem(id=2, n_stages=4, faulty=True, fault_at=1)
        for fn in (run_graph_baseline, run_imperative):
            o = fn(p)
            assert o.detected is False
            assert o.final_consistent is False
            assert o.undetected_inconsistency == 1  # молчаливая несогласованность

    def test_summaries_distinguish_conditions(self):
        problems = generate_problems(20, fault_ratio=0.5, n_stages=4)
        results = run_all_conditions(problems)
        s = {k: summarize(k, results[k]) for k in ("A", "B", "C")}
        # C обнаруживает все дефекты, baselines — ни одного
        assert s["C"].detection_rate_on_faulty == 1.0
        assert s["B"].detection_rate_on_faulty == 0.0
        assert s["A"].detection_rate_on_faulty == 0.0
        # У C нет молчаливых несогласованностей, у baselines — есть
        assert s["C"].total_undetected == 0
        assert s["B"].total_undetected > 0
        assert s["A"].total_undetected > 0
        # Итоговая согласованность C выше baseline
        assert s["C"].final_consistency_rate >= s["B"].final_consistency_rate

    def test_generate_problems_deterministic(self):
        a = generate_problems(10, fault_ratio=0.5)
        b = generate_problems(10, fault_ratio=0.5)
        assert [p.faulty for p in a] == [p.faulty for p in b]
        assert any(p.faulty for p in a) and not all(p.faulty for p in a)

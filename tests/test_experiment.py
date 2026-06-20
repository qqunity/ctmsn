from __future__ import annotations

import csv
import json

from ctmsn.experiment import (
    results_to_dicts,
    run_case,
    run_suite,
    staged_process_case,
    write_csv,
    write_json,
)


class TestExperimentHarness:
    def test_converging_case_metrics(self):
        res = run_case(staged_process_case("staged-3", 3))
        m = res.metrics
        assert m.converged is True
        assert m.final_mode == "stable"
        assert m.convergence_steps == 2
        assert m.total_steps == 2
        assert m.constraint_satisfaction_rate == 1.0
        assert m.invariant_violations == 0
        assert m.distinct_rules_fired == 2
        assert m.duration_ms >= 0.0

    def test_longer_chain_scales(self):
        res = run_case(staged_process_case("staged-5", 5))
        assert res.metrics.convergence_steps == 4
        assert res.metrics.converged is True

    def test_cyclic_case_does_not_converge(self):
        res = run_case(staged_process_case("cyclic", 3, cyclic=True), )
        m = res.metrics
        assert m.converged is False
        assert m.final_mode == "transient"
        assert m.convergence_steps is None
        # цикл упирается в лимит шагов
        assert m.total_steps == res.trace.steps.__len__()

    def test_leaky_case_violates_invariant(self):
        res = run_case(staged_process_case("leaky", 3, leaky=True))
        m = res.metrics
        assert m.invariant_violations >= 1
        assert m.constraint_satisfaction_rate < 1.0
        assert m.converged is False

    def test_run_suite_order(self):
        cases = [staged_process_case("a", 3), staged_process_case("b", 4)]
        results = run_suite(cases)
        assert [r.case for r in results] == ["a", "b"]

    def test_export_json_and_csv(self, tmp_path):
        results = run_suite([
            staged_process_case("staged-3", 3),
            staged_process_case("cyclic", 3, cyclic=True),
        ])
        jp = tmp_path / "exp.json"
        cp = tmp_path / "exp.csv"
        write_json(str(jp), results)
        write_csv(str(cp), results)

        data = json.loads(jp.read_text(encoding="utf-8"))
        assert len(data) == 2
        assert data[0]["case"] == "staged-3"
        assert data[0]["convergence_steps"] == 2

        with open(cp, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 2
        assert {r["case"] for r in rows} == {"staged-3", "cyclic"}
        assert rows[0]["final_mode"] == "stable"

    def test_results_to_dicts_shape(self):
        results = run_suite([staged_process_case("staged-3", 3)])
        d = results_to_dicts(results)[0]
        assert set(d.keys()) >= {
            "case", "final_mode", "converged", "convergence_steps",
            "total_steps", "constraint_satisfaction_rate", "invariant_violations",
            "rules_fired", "distinct_rules_fired", "duration_ms",
        }

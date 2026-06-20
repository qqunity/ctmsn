from __future__ import annotations

import pytest

pytest.importorskip("scipy", reason="требует extras: pip install -e '.[experiment]'")

from ctmsn.experiment.stats import (  # noqa: E402
    bootstrap_ci_diff,
    mann_whitney_u,
)
from ctmsn.experiment.baselines import generate_problems, run_all_conditions  # noqa: E402
from ctmsn.experiment.compare import compare_pair  # noqa: E402


class TestStats:
    def test_mann_whitney_detects_difference(self):
        a = [5, 6, 7, 8, 9, 10]
        b = [1, 2, 3, 4, 5, 6]
        res = mann_whitney_u(a, b, alternative="greater")
        assert res.p_value < 0.05
        assert res.n1 == 6 and res.n2 == 6

    def test_mann_whitney_no_difference(self):
        a = [1, 2, 3, 4, 5]
        b = [1, 2, 3, 4, 5]
        res = mann_whitney_u(a, b, alternative="two-sided")
        assert res.p_value > 0.05

    def test_bootstrap_ci_diff_positive(self):
        a = [10.0] * 20
        b = [2.0] * 20
        ci = bootstrap_ci_diff(a, b, statistic="mean", n_resamples=500, seed=1)
        assert ci.point == 8.0
        assert ci.low <= 8.0 <= ci.high

    def test_compare_pair_candidate_better(self):
        problems = generate_problems(40, fault_ratio=0.5, n_stages=4)
        results = run_all_conditions(problems)
        cmp = compare_pair(results, candidate="C", baseline="B")
        # baseline имеет больше незамеченных несогласованностей, чем кандидат
        assert cmp.mann_whitney.p_value < 0.05
        assert cmp.bootstrap.point > 0  # B − C > 0

    def test_required_sample_size_optional(self):
        statsmodels = pytest.importorskip("statsmodels")  # noqa: F841
        from ctmsn.experiment.stats import required_sample_size
        n = required_sample_size(effect_size=0.8, power=0.8, alpha=0.05)
        assert n > 0

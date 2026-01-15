from __future__ import annotations

from ctmsn.scenarios.spawn.model import build_network
from ctmsn.scenarios.spawn.constraints import build_conditions
from ctmsn.scenarios.spawn.goal import build_goal


def test_network_builds():
    net = build_network()
    assert net is not None
    assert "A" in net.concepts
    assert "B" in net.concepts
    assert "C" in net.concepts
    assert "Fish" in net.concepts
    assert "Fish_minus" in net.concepts
    assert "Fish_plus" in net.concepts


def test_conditions_build():
    conds = build_conditions()
    assert conds is not None
    assert len(conds.formulas) == 6


def test_goal_builds():
    goal = build_goal()
    assert goal is not None

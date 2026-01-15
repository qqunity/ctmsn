from __future__ import annotations

from ctmsn.scenarios.time_process.runner import run
from ctmsn.logic.tribool import TriBool


def test_run_sun_mode():
    out = run(mode="sun")
    assert out["mode"] == "sun"
    assert out["derivation"]["derived_edges_added"] > 0
    assert out["check"].ok
    assert out["forces"].value == TriBool.TRUE
    assert len(out["explain"]) > 0


def test_run_prereq_mode():
    out = run(mode="prereq")
    assert out["mode"] == "prereq"
    assert out["check"].ok
    assert out["forces"].value == TriBool.TRUE
    assert len(out["explain"]) > 0


def test_explain_composition():
    from ctmsn.scenarios.time_process.model import build_network
    from ctmsn.scenarios.time_process import derive
    from ctmsn.scenarios.time_process.explain import explain_composition

    net = build_network(mode="sun")
    derive.apply(net, mode="sun")

    expl = explain_composition(net, "sun_before", "below", "sunset")
    assert len(expl) > 0
    assert "sunset" in expl[0]
    assert "∘" in expl[0]

from __future__ import annotations

from ctmsn.scenarios.fishing.model import build_network


def test_builds():
    net = build_network()
    assert len(net.concepts) == 9
    assert "A" in net.concepts
    assert "B" in net.concepts
    assert "F" in net.concepts
    assert "F_plus" in net.concepts
    assert "F_minus" in net.concepts
    assert "W" in net.concepts
    assert "W_plus" in net.concepts
    assert "Cf_minus" in net.concepts
    assert "Cf_plus" in net.concepts


def test_edges():
    net = build_network()
    edges = list(net.facts("edge"))
    assert len(edges) > 0
    labels = {st.args[0] for st in edges}
    assert "f" in labels
    assert "h" in labels
    assert "s" in labels
    assert "j" in labels
    assert "g_minus" in labels
    assert "g_plus" in labels
    assert "catch" in labels
    assert "sf" in labels
    assert "eat" in labels
    assert "fake_plus" in labels
    assert "hook_plus" in labels
    assert "catch_sf" in labels


def test_set_facts():
    net = build_network()
    subsets = list(net.facts("subset"))
    assert len(subsets) == 2
    diffs = list(net.facts("diff"))
    assert len(diffs) == 1

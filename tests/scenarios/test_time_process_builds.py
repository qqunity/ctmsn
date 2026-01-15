from __future__ import annotations

from ctmsn.scenarios.time_process.model import build_network


def test_build_network_sun():
    net = build_network(mode="sun")
    assert "B_prime" in net.concepts
    assert "A" in net.concepts
    assert "B" in net.concepts
    assert "T" in net.concepts
    assert "T_minus" in net.concepts
    assert "T_plus" in net.concepts
    assert "horizon1" in net.concepts

    assert "edge" in net.predicates
    assert "derived_edge" in net.predicates
    assert "comp" in net.predicates
    assert "comp_expl" in net.predicates

    edges = list(net.facts("edge"))
    assert len(edges) > 0

    labels = {st.args[0] for st in edges}
    assert "before" in labels
    assert "after" in labels
    assert "sun" in labels
    assert "below" in labels
    assert "above" in labels
    assert "sunset" in labels
    assert "sunrise" in labels


def test_build_network_prereq():
    net = build_network(mode="prereq")
    assert "B_prime" in net.concepts
    assert "A" in net.concepts
    assert "B" in net.concepts

    edges = list(net.facts("edge"))
    labels = {st.args[0] for st in edges}
    assert "prerequisite" in labels
    assert "effect" in labels
    assert "h" in labels
    assert "g_minus" in labels
    assert "g_plus" in labels
    assert "h_minus" in labels
    assert "h_plus" in labels


def test_invalid_mode():
    try:
        build_network(mode="invalid")
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "mode must be" in str(e)

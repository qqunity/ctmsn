from __future__ import annotations

from ctmsn.scenarios.time_process.model import build_network
from ctmsn.scenarios.time_process import derive


def test_derive_context_edges_sun():
    net = build_network(mode="sun")
    added = derive.derive_context_edges(net, mode="sun")
    assert added > 0

    derived = list(net.facts("derived_edge"))
    labels = {st.args[0] for st in derived}
    assert "sun_before" in labels
    assert "sun_after" in labels
    assert "sun1_before" in labels
    assert "sun1_after" in labels


def test_derive_comp():
    net = build_network(mode="sun")
    derive.derive_context_edges(net, mode="sun")

    comps = derive.derive_comp(net)
    assert len(comps) > 0

    for c in comps:
        assert isinstance(c.left, str)
        assert isinstance(c.right, str)
        assert isinstance(c.result, str)
        assert isinstance(c.mid, str)


def test_apply_full_derivation():
    net = build_network(mode="sun")
    stats = derive.apply(net, mode="sun")

    assert stats["derived_edges_added"] > 0
    assert stats["comp_added"] > 0
    assert stats["comp_expl_added"] > 0

    comps = list(net.facts("comp"))
    assert len(comps) > 0


def test_derive_prereq_mode():
    net = build_network(mode="prereq")
    stats = derive.apply(net, mode="prereq")

    assert stats["derived_edges_added"] >= 0
    assert stats["comp_added"] > 0

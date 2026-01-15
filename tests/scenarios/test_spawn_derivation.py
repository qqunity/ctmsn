from __future__ import annotations

from ctmsn.scenarios.spawn.model import build_network
from ctmsn.scenarios.spawn.derive import derive_context_edges, derive_comp2, apply


def test_derive_context_edges():
    net = build_network()
    added = derive_context_edges(net)
    assert added >= 0


def test_derive_comp2():
    net = build_network()
    derive_context_edges(net)
    added = derive_comp2(net)
    assert added > 0


def test_apply():
    net = build_network()
    stats = apply(net)
    
    assert "derived_edges_added" in stats
    assert "comp2_added" in stats
    assert "compN_rethink_push_ok" in stats
    assert "compN_stageC_ok" in stats
    
    assert stats["compN_rethink_push_ok"] is True
    assert stats["compN_stageC_ok"] is True

from __future__ import annotations

from ctmsn.scenarios.fishing.model import build_network
from ctmsn.scenarios.fishing.derive import apply


def test_derive_comp2():
    net = build_network()
    apply(net)
    
    comp2_facts = list(net.facts("comp2"))
    assert len(comp2_facts) > 0
    
    comp2_set = {(st.args[0], st.args[1], st.args[2]) for st in comp2_facts}
    
    assert ("h", "g_minus", "s") in comp2_set
    assert ("h", "g_plus", "j") in comp2_set
    assert ("s", "catch", "j") in comp2_set


def test_derive_compN():
    net = build_network()
    stats = apply(net)
    
    assert stats["compN_long_ok"] is True
    
    compN_facts = list(net.facts("compN"))
    assert len(compN_facts) > 0
    
    compN_set = {(st.args[0], st.args[1]) for st in compN_facts}
    assert ("hook+∘fake+∘eat∘sf", "catch_sf") in compN_set


def test_comp2_explanations():
    net = build_network()
    apply(net)
    
    expl_facts = list(net.facts("comp2_expl"))
    assert len(expl_facts) > 0
    
    for st in expl_facts:
        left, right, result, mid = st.args
        assert isinstance(left, str)
        assert isinstance(right, str)
        assert isinstance(result, str)
        assert isinstance(mid, str)


def test_compN_explanations():
    net = build_network()
    apply(net)
    
    expl_facts = list(net.facts("compN_expl"))
    assert len(expl_facts) > 0
    
    for st in expl_facts:
        chain, result, trace = st.args
        assert isinstance(chain, str)
        assert isinstance(result, str)
        assert isinstance(trace, str)
        assert "end=" in trace

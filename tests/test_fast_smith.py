from __future__ import annotations

from ctmsn.scenarios.fast_smith.runner import run
from ctmsn.logic.tribool import TriBool


def test_fast_smith_basic():
    out = run()
    
    assert out["check"].ok is True
    assert len(out["check"].violated) == 0
    assert len(out["check"].unknown) == 0
    
    assert out["forces"].value == "true"
    
    assert out["result"].status == TriBool.TRUE
    assert "Already forced" in out["result"].explanation


def test_fast_smith_context():
    out = run()
    ctx = out["ctx0"]
    
    assert "x" in ctx
    assert "label" in ctx
    assert ctx["label"] == "h"


def test_fast_smith_network_structure():
    from ctmsn.scenarios.fast_smith.model import build_network
    
    net = build_network()
    
    required_concepts = ["A", "B", "T", "T_minus", "T_plus", "Cf_minus", "Cf_plus", "S", "J", "C"]
    for cid in required_concepts:
        assert cid in net.concepts
    
    required_predicates = ["edge", "comp", "in", "has_name", "married", "acts_like"]
    for pid in required_predicates:
        assert pid in net.predicates
    
    assert len(list(net.facts())) > 0


def test_fast_smith_compositions():
    from ctmsn.scenarios.fast_smith.model import build_network
    
    net = build_network()
    
    comp_facts = list(net.facts("comp"))
    assert len(comp_facts) == 3
    
    comp_tuples = {tuple(str(arg) if hasattr(arg, 'id') else arg for arg in s.args) for s in comp_facts}
    
    assert ("h", "g", "j") in comp_tuples
    assert ("h", "not-g", "s") in comp_tuples
    assert ("sf", "r", "jf") in comp_tuples


def test_fast_smith_behavioral_facts():
    from ctmsn.scenarios.fast_smith.model import build_network
    
    net = build_network()
    
    acts_facts = list(net.facts("acts_like"))
    assert len(acts_facts) == 3
    
    A = net.concepts["A"]
    
    acts_tuples = {(s.args[0], s.args[1]) for s in acts_facts}
    
    assert (A, "j") in acts_tuples
    assert (A, "s") in acts_tuples
    assert (A, "jf") in acts_tuples


if __name__ == "__main__":
    test_fast_smith_basic()
    test_fast_smith_context()
    test_fast_smith_network_structure()
    test_fast_smith_compositions()
    test_fast_smith_behavioral_facts()
    print("All Fast Smith tests passed!")

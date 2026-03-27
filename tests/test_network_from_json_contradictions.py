from __future__ import annotations

import json

from ctmsn.core.concept import Concept
from ctmsn.core.predicate import Predicate
from ctmsn.core.network import SemanticNetwork
from ctmsn_api.sessions import network_from_json


def _build_network_json_with_contradiction() -> str:
    """Build JSON that contains both has_ability and lacks_ability for the same args."""
    net = SemanticNetwork()
    net.add_concept(Concept(id="penguin", label="Пингвин"))
    net.add_concept(Concept(id="ability_fly", label="Летать"))
    net.add_predicate(Predicate(name="has_ability", arity=2))
    net.add_predicate(Predicate(name="lacks_ability", arity=2))

    raw = {
        "concepts": {
            "penguin": {"id": "penguin", "label": "Пингвин", "tags": [], "meta": {}},
            "ability_fly": {"id": "ability_fly", "label": "Летать", "tags": [], "meta": {}},
        },
        "predicates": {
            "has_ability": {"name": "has_ability", "arity": 2, "roles": []},
            "lacks_ability": {"name": "lacks_ability", "arity": 2, "roles": []},
        },
        "facts": [
            {"predicate": "has_ability", "args": ["penguin", "ability_fly"]},
            {"predicate": "lacks_ability", "args": ["penguin", "ability_fly"]},
        ],
    }
    return json.dumps(raw)


def test_contradictions_collected_not_raised():
    """network_from_json should return contradictions list instead of raising."""
    data = _build_network_json_with_contradiction()
    net, contradictions = network_from_json(data)

    assert len(contradictions) == 1
    assert "Противоречие" in contradictions[0]
    assert "has_ability" in contradictions[0] or "lacks_ability" in contradictions[0]


def test_first_fact_wins():
    """The first fact in the list should be kept, the contradicting one skipped."""
    data = _build_network_json_with_contradiction()
    net, contradictions = network_from_json(data)

    has_facts = list(net.facts("has_ability"))
    lacks_facts = list(net.facts("lacks_ability"))

    assert len(has_facts) == 1, "First fact (has_ability) should be kept"
    assert len(lacks_facts) == 0, "Second fact (lacks_ability) should be skipped"


def test_no_contradictions_returns_empty_list():
    """A clean network should have no contradictions."""
    raw = {
        "concepts": {
            "a": {"id": "a", "label": "A", "tags": [], "meta": {}},
        },
        "predicates": {
            "isa": {"name": "isa", "arity": 2, "roles": []},
        },
        "facts": [],
    }
    net, contradictions = network_from_json(json.dumps(raw))
    assert contradictions == []

from __future__ import annotations

import pytest

from ctmsn.core.concept import Concept
from ctmsn.core.predicate import Predicate
from ctmsn.core.network import SemanticNetwork


def _make_net() -> SemanticNetwork:
    net = SemanticNetwork()
    net.add_concept(Concept(id="penguin", label="Пингвин"))
    net.add_concept(Concept(id="ability_fly", label="Способность летать"))
    net.add_concept(Concept(id="ability_swim", label="Способность плавать"))
    net.add_predicate(Predicate(name="has_ability", arity=2))
    net.add_predicate(Predicate(name="lacks_ability", arity=2))
    net.add_predicate(Predicate(name="isa", arity=2))
    return net


def test_has_then_lacks_raises():
    net = _make_net()
    penguin = net.concepts["penguin"]
    fly = net.concepts["ability_fly"]
    net.assert_fact("has_ability", (penguin, fly))
    with pytest.raises(ValueError, match="Противоречие"):
        net.assert_fact("lacks_ability", (penguin, fly))


def test_lacks_then_has_raises():
    net = _make_net()
    penguin = net.concepts["penguin"]
    fly = net.concepts["ability_fly"]
    net.assert_fact("lacks_ability", (penguin, fly))
    with pytest.raises(ValueError, match="Противоречие"):
        net.assert_fact("has_ability", (penguin, fly))


def test_different_args_no_conflict():
    net = _make_net()
    penguin = net.concepts["penguin"]
    fly = net.concepts["ability_fly"]
    swim = net.concepts["ability_swim"]
    net.assert_fact("has_ability", (penguin, fly))
    net.assert_fact("lacks_ability", (penguin, swim))  # different arg — OK


def test_non_has_lacks_no_conflict():
    net = _make_net()
    penguin = net.concepts["penguin"]
    fly = net.concepts["ability_fly"]
    net.assert_fact("isa", (penguin, fly))
    # no counterpart predicate — should not raise

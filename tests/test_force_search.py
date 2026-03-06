from __future__ import annotations
import pytest

from ctmsn.core.concept import Concept
from ctmsn.core.predicate import Predicate
from ctmsn.core.network import SemanticNetwork
from ctmsn.param.domain import EnumDomain, RangeDomain, PredicateDomain
from ctmsn.param.variable import Variable
from ctmsn.param.context import Context
from ctmsn.logic.formula import FactAtom, Not, collect_variables, EqAtom
from ctmsn.logic.tribool import TriBool
from ctmsn.forcing.conditions import Conditions
from ctmsn.forcing.engine import ForcingEngine
from ctmsn.forcing.strategy import BruteEnumStrategy


def _make_network() -> SemanticNetwork:
    net = SemanticNetwork()
    alice = Concept("alice", "Alice")
    bob = Concept("bob", "Bob")
    carol = Concept("carol", "Carol")
    for c in (alice, bob, carol):
        net.add_concept(c)
    net.add_predicate(Predicate(name="knows", arity=2, roles=("who", "whom")))
    net.add_predicate(Predicate(name="blocked", arity=2, roles=("who", "whom")))
    net.assert_fact("knows", (alice, bob))
    net.assert_fact("knows", (bob, carol))
    net.assert_fact("blocked", (alice, carol))
    net.validate()
    return net


class TestForceSearch:
    def test_finds_extension(self):
        """Case 2: x=bob, y unassigned -> finds y=carol."""
        net = _make_network()
        domain = EnumDomain(tuple(net.concepts.values()))
        x = Variable("x", domain)
        y = Variable("y", domain)

        ctx = Context()
        ctx.set(x, net.concepts["bob"])

        phi = FactAtom("knows", (x, y))
        conds = Conditions().add(Not(FactAtom("blocked", (x, y))))

        eng = ForcingEngine(net)
        res = eng.force(ctx, phi, conds)

        assert res.status is TriBool.TRUE
        assert res.context is not None
        assert res.context.get(y).id == "carol"

    def test_already_forced(self):
        """Early return when phi is already TRUE."""
        net = _make_network()
        domain = EnumDomain(tuple(net.concepts.values()))
        x = Variable("x", domain)
        y = Variable("y", domain)

        ctx = Context()
        ctx.set(x, net.concepts["alice"])
        ctx.set(y, net.concepts["bob"])

        phi = FactAtom("knows", (x, y))
        conds = Conditions()

        eng = ForcingEngine(net)
        res = eng.force(ctx, phi, conds)

        assert res.status is TriBool.TRUE
        assert res.context is ctx
        assert res.explanation == "Already forced"

    def test_conditions_violated_for_all(self):
        """All candidates violate conditions -> FALSE."""
        net = _make_network()
        domain = EnumDomain(tuple(net.concepts.values()))
        x = Variable("x", domain)
        y = Variable("y", domain)

        ctx = Context()
        ctx.set(x, net.concepts["alice"])
        ctx.set(y, net.concepts["carol"])

        phi = FactAtom("knows", (x, y))
        conds = Conditions().add(Not(FactAtom("blocked", (x, y))))

        eng = ForcingEngine(net)
        res = eng.force(ctx, phi, conds)

        assert res.status is TriBool.FALSE

    def test_range_domain_enumeration(self):
        """RangeDomain enumerates integers correctly."""
        d = RangeDomain(1.0, 5.0, inclusive=True)
        assert list(d.enumerate_values()) == [1, 2, 3, 4, 5]

        d2 = RangeDomain(1.0, 5.0, inclusive=False)
        assert list(d2.enumerate_values()) == [2, 3, 4]

    def test_predicate_domain_skipped(self):
        """PredicateDomain variables are skipped without error."""
        net = _make_network()
        enum_domain = EnumDomain(tuple(net.concepts.values()))
        pred_domain = PredicateDomain(fn=lambda v: True, name="any")

        x = Variable("x", enum_domain)
        z = Variable("z", pred_domain)

        ctx = Context()
        ctx.set(x, net.concepts["alice"])

        phi = FactAtom("knows", (x, z))
        conds = Conditions()

        eng = ForcingEngine(net)
        res = eng.force(ctx, phi, conds)
        # z is not enumerable, so no candidates -> FALSE
        assert res.status is TriBool.FALSE

    def test_max_branch_exceeded(self):
        """Search space too large -> UNKNOWN."""
        net = _make_network()
        domain = EnumDomain(tuple(net.concepts.values()))
        x = Variable("x", domain)
        y = Variable("y", domain)

        ctx = Context()

        phi = FactAtom("knows", (x, y))
        conds = Conditions()

        eng = ForcingEngine(net)
        strategy = BruteEnumStrategy(max_branch=2)
        res = eng.force(ctx, phi, conds, strategy=strategy)

        assert res.status is TriBool.UNKNOWN
        assert "exceeds max_branch" in res.explanation

    def test_collect_variables(self):
        """collect_variables gathers all variables from a formula."""
        domain = EnumDomain(("a", "b"))
        x = Variable("x", domain)
        y = Variable("y", domain)

        f = FactAtom("knows", (x, y))
        assert collect_variables(f) == frozenset({x, y})

        f2 = Not(f)
        assert collect_variables(f2) == frozenset({x, y})

        f3 = EqAtom(x, y)
        assert collect_variables(f3) == frozenset({x, y})

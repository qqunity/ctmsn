from __future__ import annotations

from ctmsn.core.concept import Concept
from ctmsn.core.predicate import Predicate
from ctmsn.core.network import SemanticNetwork


def build_network(mode: str = "sun") -> SemanticNetwork:
    """
    Process in time (4.13). Model contains ONLY base edges.
    Derivations (sun_before/sun_after and comp) are done in derive.py.
    """
    net = SemanticNetwork()

    Bp = Concept("B_prime", "B′ (past)")
    A = Concept("A", "A / {now1}")
    B = Concept("B", "B (future)")

    horizon = Concept("horizon1", "{horizon1}")

    Tm = Concept("T_minus", "T−")
    T = Concept("T", "T")
    Tp = Concept("T_plus", "T+")

    for c in (Bp, A, B, horizon, Tm, T, Tp):
        net.add_concept(c)

    net.add_predicate(Predicate("edge", 3, roles=("label", "from", "to")))
    net.add_predicate(Predicate("derived_edge", 3, roles=("label", "from", "to")))
    net.add_predicate(Predicate("comp", 3, roles=("left", "right", "result")))
    net.add_predicate(Predicate("comp_expl", 4, roles=("left", "right", "result", "mid")))

    if mode == "sun":
        net.assert_fact("edge", ("before", Bp, A))
        net.assert_fact("edge", ("after", B, A))

        net.assert_fact("edge", ("sun", A, T))
        net.assert_fact("edge", ("below", T, Tm))
        net.assert_fact("edge", ("above", T, Tp))

        net.assert_fact("edge", ("sunset", Bp, Tm))
        net.assert_fact("edge", ("sunrise", B, Tp))

        net.assert_fact("edge", ("sun1", A, horizon))
        net.assert_fact("edge", ("below_h", horizon, Tm))
        net.assert_fact("edge", ("above_h", horizon, Tp))
        net.assert_fact("edge", ("sunset_h", Bp, Tm))
        net.assert_fact("edge", ("sunrise_h", B, Tp))

    elif mode == "prereq":
        net.assert_fact("edge", ("prerequisite", Bp, A))
        net.assert_fact("edge", ("effect", B, A))

        net.assert_fact("edge", ("h", A, T))
        net.assert_fact("edge", ("g_minus", T, Tm))
        net.assert_fact("edge", ("g_plus", T, Tp))

        net.assert_fact("edge", ("h_minus", Bp, Tm))
        net.assert_fact("edge", ("h_plus", B, Tp))

    else:
        raise ValueError("mode must be 'sun' or 'prereq'")

    net.validate()
    return net

from __future__ import annotations

from ctmsn.core.concept import Concept
from ctmsn.core.predicate import Predicate
from ctmsn.core.network import SemanticNetwork


def build_network() -> SemanticNetwork:
    """
    Canonical Fast Smith model close to the figure:
    Nodes: A, B, T, T-, T+, Cf-, Cf+
    Morphisms/labels: f, s, sf, h, g, not-g, r, j, jf
    Plus story-level facts about name change and marriage.
    """

    net = SemanticNetwork()

    A = Concept("A", "Smith (A)")
    B = Concept("B", "Pre-state (B)")

    T = Concept("T", "Time/Transition (T)")
    T_plus = Concept("T_plus", "T+")
    T_minus = Concept("T_minus", "T-")

    Cf_minus = Concept("Cf_minus", "C_f-")
    Cf_plus = Concept("Cf_plus", "C_f+")

    S = Concept("S", "Spouse (S)")
    J = Concept("J", "Jones (J)")
    C = Concept("C", "Spouse (C)")

    for c in (A, B, T, T_plus, T_minus, Cf_minus, Cf_plus, S, J, C):
        net.add_concept(c)

    net.add_predicate(Predicate("edge", 3, roles=("label", "from", "to")))

    net.add_predicate(Predicate("comp", 3, roles=("left", "right", "result")))

    net.add_predicate(Predicate("in", 2, roles=("elem", "set")))

    net.add_predicate(Predicate("has_name", 2, roles=("person", "name")))
    net.add_predicate(Predicate("married", 2, roles=("person", "spouse")))

    net.add_predicate(Predicate("acts_like", 2, roles=("node", "label")))

    net.assert_fact("edge", ("f", A, B))

    net.assert_fact("edge", ("s", A, T_minus))

    net.assert_fact("edge", ("sf", B, Cf_minus))

    net.assert_fact("edge", ("h", A, T))

    net.assert_fact("edge", ("j", A, T_plus))

    net.assert_fact("edge", ("g", T, T_plus))

    net.assert_fact("edge", ("not-g", T, T_minus))

    net.assert_fact("edge", ("r", T_minus, T_plus))

    net.assert_fact("edge", ("r∘sf", Cf_minus, Cf_plus))

    net.assert_fact("edge", ("incl", Cf_minus, T_minus))
    net.assert_fact("edge", ("incl", Cf_plus, T_plus))

    net.assert_fact("comp", ("h", "g", "j"))

    net.assert_fact("comp", ("h", "not-g", "s"))

    net.assert_fact("comp", ("sf", "r", "jf"))

    net.assert_fact("acts_like", (A, "j"))
    net.assert_fact("acts_like", (A, "s"))
    net.assert_fact("acts_like", (A, "jf"))

    net.assert_fact("married", (A, S))
    net.assert_fact("has_name", (A, J))
    net.assert_fact("married", (J, C))

    net.assert_fact("in", (T_minus, T))
    net.assert_fact("in", (T_plus, T))

    net.validate()
    return net

from __future__ import annotations

from ctmsn.core.concept import Concept
from ctmsn.core.predicate import Predicate
from ctmsn.core.network import SemanticNetwork


def build_network() -> SemanticNetwork:
    """
    Fishing (4.14) — canonical graph only.
    No comp(...) facts here; they are derived.
    """

    net = SemanticNetwork()

    # Nodes
    A = Concept("A", "A (event state)")
    B = Concept("B", "B (event state)")

    F = Concept("F", "Fish (F)")
    Fp = Concept("F_plus", "F+ (caught fish)")
    Fm = Concept("F_minus", "F- (free fish)")

    W = Concept("W", "Worm (W)")
    Wp = Concept("W_plus", "W+ (fake worm/bait)")

    Cf_m = Concept("Cf_minus", "C_f-")
    Cf_p = Concept("Cf_plus", "C_f+")

    for c in (A, B, F, Fp, Fm, W, Wp, Cf_m, Cf_p):
        net.add_concept(c)

    # Predicates
    net.add_predicate(Predicate("edge", 3, roles=("label", "from", "to")))

    # Set/partition meta (optional but canonical w.r.t. text)
    net.add_predicate(Predicate("subset", 2, roles=("sub", "sup")))
    net.add_predicate(Predicate("diff", 3, roles=("result", "set", "minus")))   # result = set \ minus

    # Derived facts (populated in derive.py)
    net.add_predicate(Predicate("derived_edge", 3, roles=("label", "from", "to")))
    net.add_predicate(Predicate("comp2", 3, roles=("left", "right", "result")))
    net.add_predicate(Predicate("compN", 2, roles=("chain", "result")))         # chain encoded as string
    net.add_predicate(Predicate("comp2_expl", 4, roles=("left", "right", "result", "mid")))
    net.add_predicate(Predicate("compN_expl", 3, roles=("chain", "result", "mids")))  # mids encoded

    # --- Graph edges (as in figure/text) ---
    net.assert_fact("edge", ("f", B, A))

    net.assert_fact("edge", ("h", A, F))
    net.assert_fact("edge", ("s", A, Fm))
    net.assert_fact("edge", ("j", A, Fp))

    net.assert_fact("edge", ("g_minus", F, Fm))
    net.assert_fact("edge", ("g_plus", F, Fp))

    net.assert_fact("edge", ("catch", Fm, Fp))

    net.assert_fact("edge", ("sf", B, Cf_m))

    net.assert_fact("edge", ("incl", Cf_m, Fm))
    net.assert_fact("edge", ("incl", Cf_p, Fp))

    net.assert_fact("edge", ("eat", Cf_m, W))

    net.assert_fact("edge", ("fake_plus", W, Wp))
    net.assert_fact("edge", ("fake_minus", W, W))      # "check authenticity"

    net.assert_fact("edge", ("hook_minus", W, Cf_m))
    net.assert_fact("edge", ("hook_plus", Wp, Cf_p))

    # Named "result arrow" for the canonical long equality:
    # hook+ ∘ fake+ ∘ eat ∘ sf = catch ∘ sf
    # We'll name (catch ∘ sf) as a direct arrow 'catch_sf' : B -> Cf_plus.
    net.assert_fact("edge", ("catch_sf", B, Cf_p))

    # --- Set facts from text ---
    net.assert_fact("subset", (Fp, F))
    net.assert_fact("subset", (Fm, F))
    net.assert_fact("diff", (Fm, F, Fp))  # F- = F \ F+

    net.validate()
    return net

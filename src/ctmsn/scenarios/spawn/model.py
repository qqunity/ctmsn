from __future__ import annotations

from ctmsn.core.concept import Concept
from ctmsn.core.predicate import Predicate
from ctmsn.core.network import SemanticNetwork


def build_network() -> SemanticNetwork:
    """
    Fish spawning problem (4.15) — canonical graph only.
    No composition facts are stored here.
    """

    net = SemanticNetwork()

    # --- Nodes / Concepts ---
    A = Concept("A", "Stage A")
    B = Concept("B", "Stage B (later than A)")
    C = Concept("C", "Stage C (later than B)")

    Fish = Concept("Fish", "Fish")
    Fish_m = Concept("Fish_minus", "Fish- (not eat eggs)")
    Fish_p = Concept("Fish_plus", "Fish+ (eat eggs)")

    Cf_m = Concept("Cf_minus", "C_f- (not eat eggs under f)")
    Cf_p = Concept("Cf_plus", "C_f+ (eat eggs under f)")
    Cf_p_fe = Concept("Cf_plus_fe", "(C_f+)_fe (eat eggs under f∘e)")

    for cpt in (A, B, C, Fish, Fish_m, Fish_p, Cf_m, Cf_p, Cf_p_fe):
        net.add_concept(cpt)

    # --- Predicates ---
    net.add_predicate(Predicate("edge", 3, roles=("label", "from", "to")))

    # meta about sets/partitions (optional)
    net.add_predicate(Predicate("subset", 2, roles=("sub", "sup")))

    # derived/logic layer (filled by derive.py)
    net.add_predicate(Predicate("derived_edge", 3, roles=("label", "from", "to")))
    net.add_predicate(Predicate("comp2", 3, roles=("left", "right", "result")))
    net.add_predicate(Predicate("comp2_expl", 4, roles=("left", "right", "result", "mid")))
    net.add_predicate(Predicate("compN", 2, roles=("chain", "result")))
    net.add_predicate(Predicate("compN_expl", 3, roles=("chain", "result", "trace")))

    # --- Evolvents (time progression) ---
    net.assert_fact("edge", ("f", B, A))
    net.assert_fact("edge", ("e", C, B))

    # --- Base "fish" mapping at A ---
    net.assert_fact("edge", ("fish", A, Fish))

    # --- eat / not-eat classification ---
    net.assert_fact("edge", ("not_eat", Fish, Fish_m))
    net.assert_fact("edge", ("eat", Fish, Fish_p))

    # named results from the text:
    # spawner = not-eat ∘ fish ; milter = eat ∘ fish
    net.assert_fact("edge", ("spawner", A, Fish_m))
    net.assert_fact("edge", ("milter", A, Fish_p))

    # --- behaviour operators ---
    net.assert_fact("edge", ("push", Fish_p, Fish_m))
    net.assert_fact("edge", ("rethink", Fish_m, Fish_p))

    # --- context inclusions (||) ---
    net.assert_fact("edge", ("incl", Cf_m, Fish_m))
    net.assert_fact("edge", ("incl", Cf_p, Fish_p))
    net.assert_fact("edge", ("incl", Cf_p_fe, Fish_p))

    # --- named "stage B" and "stage C" result arrows (as in text) ---
    # After development f:
    net.assert_fact("edge", ("spawner_f", B, Fish_m))
    net.assert_fact("edge", ("milter_f", B, Fish_p))

    # After applying e (stage C):
    net.assert_fact("edge", ("spawner_fe", C, Fish_m))  # (spawner_f)_e
    net.assert_fact("edge", ("milter_fe", C, Fish_p))   # (milter_f)_e

    # (Optional but useful) constraints about subsets
    net.assert_fact("subset", (Fish_m, Fish))
    net.assert_fact("subset", (Fish_p, Fish))

    net.validate()
    return net

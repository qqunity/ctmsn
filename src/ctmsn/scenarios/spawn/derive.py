from __future__ import annotations

from typing import Dict, List, Tuple

from ctmsn.core.concept import Concept
from ctmsn.core.network import SemanticNetwork


def _all_edges(net: SemanticNetwork) -> list[tuple[str, Concept, Concept, str]]:
    out = []
    for st in net.facts("edge"):
        lab, s, d = st.args  # type: ignore[misc]
        out.append((lab, s, d, "edge"))
    for st in net.facts("derived_edge"):
        lab, s, d = st.args  # type: ignore[misc]
        out.append((lab, s, d, "derived_edge"))
    return out


def _direct_set(net: SemanticNetwork) -> set[tuple[str, str, str]]:
    return {(lab, s.id, d.id) for (lab, s, d, _k) in _all_edges(net)}


def derive_context_edges(net: SemanticNetwork) -> int:
    """
    D1: derive time-indexed arrows, if not present, using:
      X -f-> A and A -label-> Z  => X -label_f-> Z
      Y -e-> X and X -label_f-> Z => Y -label_fe-> Z
    We only derive the specific ones we need for canonical equalities.
    """
    added = 0
    direct = _direct_set(net)

    def add(label: str, src: str, dst: str):
        nonlocal added, direct
        if (label, src, dst) not in direct:
            net.assert_fact("derived_edge", (label, net.concepts[src], net.concepts[dst]))
            direct.add((label, src, dst))
            added += 1

    # Read core ids
    A, B, C = "A", "B", "C"
    Fish = "Fish"
    Fish_m = "Fish_minus"
    Fish_p = "Fish_plus"

    # If B -f-> A and A -fish-> Fish => fish_f: B -> Fish
    if ("f", B, A) in direct and ("fish", A, Fish) in direct:
        add("fish_f", B, Fish)

    # If B -f-> A and A -spawner-> Fish- => spawner_f: B -> Fish-
    if ("f", B, A) in direct and ("spawner", A, Fish_m) in direct:
        add("spawner_f", B, Fish_m)

    # If B -f-> A and A -milter-> Fish+ => milter_f: B -> Fish+
    if ("f", B, A) in direct and ("milter", A, Fish_p) in direct:
        add("milter_f", B, Fish_p)

    # Now extend by e: C -e-> B and B -spawner_f-> Fish- => spawner_fe: C -> Fish-
    if ("e", C, B) in direct and ("spawner_f", B, Fish_m) in direct:
        add("spawner_fe", C, Fish_m)

    if ("e", C, B) in direct and ("milter_f", B, Fish_p) in direct:
        add("milter_fe", C, Fish_p)

    return added


def derive_comp2(net: SemanticNetwork) -> int:
    """
    D2.1: derive comp2(left,right,result) if 2-step path matches and named result arrow exists.
    """
    edges = _all_edges(net)

    by_pair: Dict[Tuple[str, str], List[str]] = {}
    for lab, s, d, _k in edges:
        by_pair.setdefault((s.id, d.id), []).append(lab)

    before = len(list(net.facts("comp2")))
    before_expl = len(list(net.facts("comp2_expl")))

    seen = set()
    for left, X, mid, _k1 in edges:
        for right, mid2, Z, _k2 in edges:
            if mid2.id != mid.id:
                continue
            for result in by_pair.get((X.id, Z.id), []):
                key = (left, right, result, mid.id)
                if key in seen:
                    continue
                seen.add(key)
                net.assert_fact("comp2", (left, right, result))
                net.assert_fact("comp2_expl", (left, right, result, mid.id))

    after = len(list(net.facts("comp2")))
    after_expl = len(list(net.facts("comp2_expl")))
    return (after - before) + (after_expl - before_expl)


def _adj(net: SemanticNetwork) -> Dict[Tuple[str, str], List[str]]:
    adj: Dict[Tuple[str, str], List[str]] = {}
    for lab, s, d, _k in _all_edges(net):
        adj.setdefault((s.id, lab), []).append(d.id)
    return adj


def derive_compN(net: SemanticNetwork, start: str, chain: list[str], result_label: str, chain_name: str) -> bool:
    """
    D2.2: check N-step chain and if there is a named result arrow start -result_label-> end,
    record compN(chain_name, result_label) with trace.
    """
    adj = _adj(net)
    direct = _direct_set(net)

    cur = {start}
    trace_parts: list[str] = [f"start={start}"]
    for lab in chain:
        nxt = set()
        for s in cur:
            for d in adj.get((s, lab), []):
                nxt.add(d)
        trace_parts.append(f"{lab}->{sorted(nxt)}")
        cur = nxt
        if not cur:
            return False

    for end in cur:
        if (result_label, start, end) in direct:
            net.assert_fact("compN", (chain_name, result_label))
            net.assert_fact("compN_expl", (chain_name, result_label, "; ".join(trace_parts) + f"; end={end}"))
            return True
    return False


def apply(net: SemanticNetwork) -> dict[str, object]:
    """
    Apply all derivations needed for canonical equalities in 4.15.
    """
    stats: dict[str, object] = {}

    stats["derived_edges_added"] = derive_context_edges(net)
    stats["comp2_added"] = derive_comp2(net)

    # Long equality in text:
    # rethink ∘ push ∘ milter_f = milter_f
    ok1 = derive_compN(
        net=net,
        start="B",
        chain=["milter_f", "push", "rethink"],
        result_label="milter_f",
        chain_name="rethink∘push∘milter_f",
    )
    stats["compN_rethink_push_ok"] = ok1

    # For stage C condition: (rethink ∘ spawner_f)_e = (milter_f)_e
    # We'll encode it as: first derive "rethink_spawner_f" by comp2, then time-extend by e.
    #
    # We need a named arrow rethink_spawner_f : B -> Fish_plus and rethink_spawner_fe : C -> Fish_plus.
    # Add them as derived edges if they exist as a path + named arrow.
    # (In canonical "equation style", you either name them explicitly or derive them; here we name as derived.)
    #
    # Step A: if comp2(spawner_f, rethink, milter_f) holds, then "rethink∘spawner_f = milter_f".
    # That already implies the e-extended equality, but we'll still check a compN form at stage C:
    ok2 = derive_compN(
        net=net,
        start="C",
        chain=["e", "spawner_f", "rethink"],   # note: e brings C->B, then apply spawner_f, then rethink
        result_label="milter_fe",
        chain_name="(rethink∘spawner_f)_e",
    )
    stats["compN_stageC_ok"] = ok2

    return stats

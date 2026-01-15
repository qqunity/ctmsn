from __future__ import annotations

from dataclasses import dataclass

from ctmsn.core.concept import Concept
from ctmsn.core.network import SemanticNetwork


@dataclass(frozen=True)
class DerivedComp:
    left: str
    right: str
    result: str
    X: str
    mid: str
    Z: str


def _all_edges(net: SemanticNetwork) -> list[tuple[str, Concept, Concept, str]]:
    """
    Return list of edges as tuples: (label, src, dst, kind)
    kind ∈ {"edge","derived_edge"}
    """
    out = []
    for st in net.facts("edge"):
        label, src, dst = st.args
        out.append((label, src, dst, "edge"))
    for st in net.facts("derived_edge"):
        label, src, dst = st.args
        out.append((label, src, dst, "derived_edge"))
    return out


def derive_context_edges(net: SemanticNetwork, mode: str) -> int:
    """
    D1: derive sun_before/sun_after (and sun1_before/sun1_after) from before/after and sun/sun1.
    Adds derived_edge facts.
    """
    added = 0

    def C(cid: str) -> Concept:
        return net.concepts[cid]

    Bp, A, B = C("B_prime"), C("A"), C("B")
    T = C("T")

    base = [(l, s, d) for (l, s, d, k) in _all_edges(net) if k == "edge"]

    def has_edge(label: str, s: Concept, d: Concept) -> bool:
        for l, ss, dd in base:
            if l == label and ss.id == s.id and dd.id == d.id:
                return True
        for st in net.facts("derived_edge"):
            l2, ss2, dd2 = st.args
            if l2 == label and ss2.id == s.id and dd2.id == d.id:
                return True
        return False

    def add_derived(label: str, s: Concept, d: Concept):
        nonlocal added
        if not has_edge(label, s, d):
            net.assert_fact("derived_edge", (label, s, d))
            added += 1

    if mode == "sun":
        horizon = C("horizon1")

        if any(l == "before" and s.id == Bp.id and d.id == A.id for l, s, d in base) and \
           any(l == "sun" and s.id == A.id and d.id == T.id for l, s, d in base):
            add_derived("sun_before", Bp, T)

        if any(l == "after" and s.id == B.id and d.id == A.id for l, s, d in base) and \
           any(l == "sun" and s.id == A.id and d.id == T.id for l, s, d in base):
            add_derived("sun_after", B, T)

        if any(l == "before" and s.id == Bp.id and d.id == A.id for l, s, d in base) and \
           any(l == "sun1" and s.id == A.id and d.id == horizon.id for l, s, d in base):
            add_derived("sun1_before", Bp, horizon)

        if any(l == "after" and s.id == B.id and d.id == A.id for l, s, d in base) and \
           any(l == "sun1" and s.id == A.id and d.id == horizon.id for l, s, d in base):
            add_derived("sun1_after", B, horizon)

    elif mode == "prereq":
        if any(l == "prerequisite" and d.id == A.id for l, s, d in base) and \
           any(l == "h" and s.id == A.id and d.id == T.id for l, s, d in base):
            add_derived("h_before", Bp, T)

        if any(l == "effect" and d.id == A.id for l, s, d in base) and \
           any(l == "h" and s.id == A.id and d.id == T.id for l, s, d in base):
            add_derived("h_after", B, T)

    else:
        raise ValueError("mode must be 'sun' or 'prereq'")

    return added


def derive_comp(net: SemanticNetwork) -> list[DerivedComp]:
    """
    D2: derive comp(left, right, result) when:
      edge/derived_edge(left, X, mid) and edge/derived_edge(right, mid, Z) and
      edge/derived_edge(result, X, Z)
    Also records comp_expl(left, right, result, mid).
    """
    edges = _all_edges(net)

    by_pair: dict[tuple[str, str], list[str]] = {}
    for label, src, dst, _ in edges:
        by_pair.setdefault((src.id, dst.id), []).append(label)

    derived: list[DerivedComp] = []
    seen: set[tuple[str, str, str, str]] = set()

    for left, X, mid, _k1 in edges:
        for right, mid2, Z, _k2 in edges:
            if mid2.id != mid.id:
                continue
            for result in by_pair.get((X.id, Z.id), []):
                key = (left, right, result, mid.id)
                if key in seen:
                    continue
                seen.add(key)
                derived.append(DerivedComp(left, right, result, X.id, mid.id, Z.id))

    return derived


def apply(net: SemanticNetwork, mode: str) -> dict[str, int]:
    """
    Apply derivations:
      - derive_context_edges (D1)
      - derive_comp (D2) and store comp + comp_expl
    """
    added_edges = derive_context_edges(net, mode=mode)

    before_comp = len(list(net.facts("comp")))
    before_expl = len(list(net.facts("comp_expl")))

    for d in derive_comp(net):
        net.assert_fact("comp", (d.left, d.right, d.result))
        net.assert_fact("comp_expl", (d.left, d.right, d.result, d.mid))

    after_comp = len(list(net.facts("comp")))
    after_expl = len(list(net.facts("comp_expl")))

    return {
        "derived_edges_added": added_edges,
        "comp_added": after_comp - before_comp,
        "comp_expl_added": after_expl - before_expl,
    }

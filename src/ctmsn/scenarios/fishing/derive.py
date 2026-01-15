from __future__ import annotations

from typing import Dict, List, Tuple

from ctmsn.core.concept import Concept
from ctmsn.core.network import SemanticNetwork


def _edges(net: SemanticNetwork) -> list[tuple[str, Concept, Concept, str]]:
    out = []
    for st in net.facts("edge"):
        lab, s, d = st.args  # type: ignore[misc]
        out.append((lab, s, d, "edge"))
    for st in net.facts("derived_edge"):
        lab, s, d = st.args  # type: ignore[misc]
        out.append((lab, s, d, "derived_edge"))
    return out


def derive_comp2(net: SemanticNetwork) -> int:
    """
    Canonical 2-step composition equality:
    If X -left-> mid and mid -right-> Z and there exists X -result-> Z,
    then comp2(left, right, result) i.e. right ∘ left = result.
    Also stores comp2_expl(left,right,result,mid).
    """
    edges = _edges(net)

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
            # does X->Z have some named result label?
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
    """
    adjacency: (src_id, label) -> [dst_ids]
    """
    adj: Dict[Tuple[str, str], List[str]] = {}
    for lab, s, d, _k in _edges(net):
        adj.setdefault((s.id, lab), []).append(d.id)
    return adj


def check_chain(net: SemanticNetwork, start_id: str, chain: list[str]) -> tuple[bool, list[str], list[str]]:
    """
    Follows chain of labels from start_id.
    Returns (ok, end_ids, mids_path_debug).
    """
    adj = _adj(net)
    cur = {start_id}
    mids_debug: list[str] = []
    for lab in chain:
        nxt = set()
        for s in cur:
            for d in adj.get((s, lab), []):
                nxt.add(d)
        mids_debug.append(f"{lab}: {sorted(nxt)}")
        cur = nxt
        if not cur:
            return (False, [], mids_debug)
    return (True, sorted(cur), mids_debug)


def derive_compN(net: SemanticNetwork, start: str, chain: list[str], result_label: str, chain_name: str | None = None) -> bool:
    """
    Canonical N-step equality:
      right_n ∘ ... ∘ right_1 = result_label
    for a given start node.

    We record it as:
      compN("<chain-encoded>", result_label)
      compN_expl("<chain-encoded>", result_label, "<ends/mids debug>")

    Additionally, we materialize the composed arrow as derived_edge(chain_name, start, end)
    if chain_name is provided and the end is unique.
    """
    ok, ends, mids_dbg = check_chain(net, start, chain)
    chain_enc = chain_name or " ∘ ".join(chain)

    if not ok:
        return False

    # We need existence of a named result arrow from start to some end:
    # edge(result_label, start, end)
    direct = {(lab, s.id, d.id) for (lab, s, d, _k) in _edges(net)}
    for end in ends:
        if (result_label, start, end) in direct:
            net.assert_fact("compN", (chain_enc, result_label))
            net.assert_fact("compN_expl", (chain_enc, result_label, "; ".join(mids_dbg) + f"; end={end}"))

            # materialize the composed arrow (optional, but very useful for later forcing)
            if chain_name is not None and len(ends) == 1:
                end_id = ends[0]
                net.assert_fact("derived_edge", (chain_name, net.concepts[start], net.concepts[end_id]))
            return True

    return False


def apply(net: SemanticNetwork) -> dict[str, int | bool]:
    """
    Apply all derivations needed for the Fishing scenario.
    """
    stats = {}
    stats["comp2_added"] = derive_comp2(net)

    # Canonical long equality:
    # hook+ ∘ fake+ ∘ eat ∘ sf = catch ∘ sf
    # start is B, result arrow is catch_sf : B -> Cf_plus
    ok_long = derive_compN(
        net=net,
        start="B",
        chain=["sf", "eat", "fake_plus", "hook_plus"],
        result_label="catch_sf",
        chain_name="hook+∘fake+∘eat∘sf",
    )
    stats["compN_long_ok"] = ok_long

    return stats

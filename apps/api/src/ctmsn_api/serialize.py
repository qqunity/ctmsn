from __future__ import annotations
from typing import Any

def serialize(net) -> dict[str, Any]:
    nodes = []
    for cid, c in net.concepts.items():
        nodes.append({
            "id": cid, 
            "label": getattr(c, "label", None) or getattr(c, "title", None) or getattr(c, "name", None) or cid,
            "tags": list(c.tags) if hasattr(c, 'tags') else []
        })
    
    predicates = []
    for pname, pred in net.predicates.items():
        predicates.append({"name": pname, "arity": pred.arity})

    edges = []
    def add(pred: str, kind: str):
        if pred not in net.predicates:
            return
        for st in net.facts(pred):
            label, src, dst = st.args
            src_id = src.id if hasattr(src, 'id') else str(src)
            dst_id = dst.id if hasattr(dst, 'id') else str(dst)
            edges.append({
                "id": f"{pred}:{label}:{src_id}->{dst_id}",
                "label": str(label),
                "source": src_id,
                "target": dst_id,
                "kind": kind,
            })

    def add_binary(pred: str, kind: str, label: str | None = None):
        if pred not in net.predicates:
            return
        for st in net.facts(pred):
            src, dst = st.args
            edge_label = label or pred
            src_id = src.id if hasattr(src, 'id') else str(src)
            dst_id = dst.id if hasattr(dst, 'id') else str(dst)
            edges.append({
                "id": f"{pred}:{src_id}->{dst_id}",
                "label": edge_label,
                "source": src_id,
                "target": dst_id,
                "kind": kind,
            })

    add("edge", "edge")
    add("derived_edge", "derived")
    add_binary("married", "relation", "married")
    add_binary("has_name", "relation", "has_name")
    
    for pname, pred in net.predicates.items():
        if pname in ["edge", "derived_edge", "married", "has_name", "comp", "comp_expl", "comp2", "comp2_expl", "compN", "compN_expl"]:
            continue
        if pred.arity == 2:
            add_binary(pname, "relation", pname)

    equations = []
    if "comp2" in net.predicates:
        for st in net.facts("comp2"):
            left, right, result = st.args
            equations.append({"kind":"comp2","left":str(left),"right":str(right),"result":str(result)})
    if "compN" in net.predicates:
        for st in net.facts("compN"):
            chain, result = st.args
            equations.append({"kind":"compN","chain":str(chain),"result":str(result)})

    node_ids = {n["id"] for n in nodes}
    edges = [e for e in edges if e["source"] in node_ids and e["target"] in node_ids]

    traces = {"comp2": [], "compN": []}
    if "comp2_expl" in net.predicates:
        for st in net.facts("comp2_expl"):
            left, right, result, mid = st.args
            traces["comp2"].append({"left":str(left),"right":str(right),"result":str(result),"mid":str(mid)})
    if "compN_expl" in net.predicates:
        for st in net.facts("compN_expl"):
            chain, result, trace = st.args
            traces["compN"].append({"chain":str(chain),"result":str(result),"trace":str(trace)})

    return {"nodes": nodes, "edges": edges, "equations": equations, "traces": traces, "predicates": predicates}

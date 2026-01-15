from __future__ import annotations

from ctmsn.core.network import SemanticNetwork


def explain_comp2(net: SemanticNetwork, left: str, right: str, result: str) -> list[str]:
    lines = []
    for st in net.facts("comp2_expl"):
        l, r, res, mid = st.args  # type: ignore[misc]
        if l == left and r == right and res == result:
            lines.append(f"{res} = {right} ∘ {left} (через {mid})")
    if not lines:
        lines.append(f"Нет доказательства comp2 для {result} = {right} ∘ {left}")
    return lines


def explain_compN(net: SemanticNetwork, chain: str, result: str) -> list[str]:
    lines = []
    for st in net.facts("compN_expl"):
        ch, res, trace = st.args  # type: ignore[misc]
        if ch == chain and res == result:
            lines.append(f"{result} = {chain} (trace: {trace})")
    if not lines:
        lines.append(f"Нет доказательства compN для {result} = {chain}")
    return lines

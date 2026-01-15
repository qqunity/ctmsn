from __future__ import annotations

from ctmsn.core.network import SemanticNetwork


def explain_composition(net: SemanticNetwork, left: str, right: str, result: str) -> list[str]:
    """
    Reads comp_expl facts and formats short explanations.
    """
    lines: list[str] = []
    for st in net.facts("comp_expl"):
        l, r, res, mid = st.args
        if l == left and r == right and res == result:
            lines.append(f"{res} = {right} ∘ {left} (через узел {mid})")
    if not lines:
        lines.append(f"Нет объяснения для {result} = {right} ∘ {left}")
    return lines

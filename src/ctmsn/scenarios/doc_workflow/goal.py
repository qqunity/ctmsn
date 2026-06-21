from __future__ import annotations

from ctmsn.core.network import SemanticNetwork
from ctmsn.logic.formula import And, FactAtom
from ctmsn.scenarios.doc_workflow.params import build_variables


def build_goal(net: SemanticNetwork) -> And:
    """Цель: документ опубликован и назначен подобранный рецензент.

    Цель ложна на начальной сети (документ — черновик) и становится достижимой
    после прохождения переходов; параметр reviewer подбирается форсированием.
    """
    doc = net.concepts["doc"]
    published = net.concepts["published"]
    v, _ = build_variables(net)

    return And((
        FactAtom("status", (doc, published)),
        FactAtom("assigned", (doc, v.reviewer)),
    ))

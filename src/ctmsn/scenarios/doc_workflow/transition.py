from __future__ import annotations

from ctmsn.core.network import SemanticNetwork
from ctmsn.forcing.conditions import Conditions
from ctmsn.logic.formula import FactAtom, Or
from ctmsn.scenarios.doc_workflow.model import STATUSES
from ctmsn.transition.invariant import invariants
from ctmsn.transition.rule import AddFact, RetractFact, TransitionRule


def build_rules(net: SemanticNetwork) -> list[TransitionRule]:
    """Правила переходов документооборота.

    Три автономных правила (submit/approve/publish) ведут документ к устойчивому
    режиму «опубликован». Правило reject — событийное (on_event="reject"):
    возвращает документ из рассмотрения в черновик.
    """
    doc = net.concepts["doc"]

    def g(stage: str) -> FactAtom:
        return FactAtom("status", (doc, net.concepts[stage]))

    def move(src: str, dst: str):
        return (RetractFact("status", ("doc", src)), AddFact("status", ("doc", dst)))

    return [
        TransitionRule("submit", guard=g("draft"), effect=move("draft", "review")),
        TransitionRule("approve", guard=g("review"), effect=move("review", "approved")),
        TransitionRule("publish", guard=g("approved"), effect=move("approved", "published")),
        # Приоритет выше, чтобы при событии reject он выбирался раньше autonomous-правил.
        TransitionRule("reject", guard=g("review"), effect=move("review", "draft"),
                       priority=1, on_event="reject"),
    ]


def build_invariants(net: SemanticNetwork) -> Conditions:
    """Денотационный инвариант: документ всегда находится в одном из известных статусов."""
    doc = net.concepts["doc"]
    return invariants(
        Or(tuple(FactAtom("status", (doc, net.concepts[s])) for s in STATUSES))
    )

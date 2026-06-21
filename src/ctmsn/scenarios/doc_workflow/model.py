from __future__ import annotations

from ctmsn.core.concept import Concept
from ctmsn.core.network import SemanticNetwork
from ctmsn.core.predicate import Predicate

STATUSES = ("draft", "review", "approved", "published", "rejected")


def build_network() -> SemanticNetwork:
    """Предметная область «Документооборот».

    Документ проходит статусы draft -> review -> approved -> published,
    находясь в каждый момент ровно в одном статусе (денотационный инвариант).
    Статус rejected — побочная ветвь (возврат на доработку по событию).
    """
    net = SemanticNetwork()

    net.add_concept(Concept("doc", "Документ"))
    net.add_concept(Concept("draft", "Черновик"))
    net.add_concept(Concept("review", "На рассмотрении"))
    net.add_concept(Concept("approved", "Утверждён"))
    net.add_concept(Concept("published", "Опубликован"))
    net.add_concept(Concept("rejected", "Отклонён"))
    net.add_concept(Concept("alice", "Рецензент Алиса"))
    net.add_concept(Concept("bob", "Рецензент Боб"))

    net.add_predicate(Predicate("status", 2, roles=("doc", "stage")))
    net.add_predicate(Predicate("assigned", 2, roles=("doc", "reviewer")))

    # Начальное состояние: документ — черновик, назначен рецензент Алиса.
    net.assert_fact("status", (net.concepts["doc"], net.concepts["draft"]))
    net.assert_fact("assigned", (net.concepts["doc"], net.concepts["alice"]))

    net.validate()
    return net

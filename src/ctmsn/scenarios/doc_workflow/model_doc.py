from __future__ import annotations

from ctmsn.io.model import Model
from ctmsn.scenarios.doc_workflow.model import build_network
from ctmsn.scenarios.doc_workflow.transition import build_invariants, build_rules


def build_model() -> Model:
    """Полная декларативная модель сценария: сеть + правила + инварианты.

    Пригодна для сериализации в JSON/YAML и round-trip через ctmsn.io
    (dump_model / load_model).
    """
    net = build_network()
    return Model(
        network=net,
        rules=build_rules(net),
        invariants=build_invariants(net),
    )

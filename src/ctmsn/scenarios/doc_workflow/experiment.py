from __future__ import annotations

from ctmsn.experiment.case import ExperimentCase
from ctmsn.scenarios.doc_workflow.model import build_network
from ctmsn.scenarios.doc_workflow.transition import build_invariants, build_rules


def build_case() -> ExperimentCase:
    """Экспериментальный кейс сценария для сбора метрик (Convergence Time, CSR и др.)."""
    net = build_network()
    return ExperimentCase(
        name="doc_workflow",
        net=net,
        rules=build_rules(net),
        invariants=build_invariants(net),
    )

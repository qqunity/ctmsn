from __future__ import annotations

import pytest

from ctmsn.core.concept import Concept
from ctmsn.core.network import SemanticNetwork
from ctmsn.core.predicate import Predicate
from ctmsn.forcing.conditions import Conditions
from ctmsn.logic.formula import And, FactAtom, Not, Or
from ctmsn.transition.rule import AddFact, RetractFact, TransitionRule
from ctmsn.io import (
    Model,
    dump_model,
    dump_network,
    dumps_model_json,
    formula_from_dict,
    formula_to_dict,
    load_model,
    load_network,
    loads_model_json,
    rule_from_dict,
    rule_to_dict,
)


def _staged_net() -> SemanticNetwork:
    net = SemanticNetwork()
    for cid in ("obj", "a", "b", "c"):
        net.add_concept(Concept(id=cid, label=cid.upper(), tags=frozenset({"stage"} if cid != "obj" else set())))
    net.add_predicate(Predicate(name="at", arity=2))
    net.assert_fact("at", (net.concepts["obj"], net.concepts["a"]))
    return net


def _facts_set(net: SemanticNetwork):
    return {(f.predicate, tuple(getattr(a, "id", a) for a in f.args)) for f in net.facts()}


class TestNetworkRoundtrip:
    def test_network_roundtrip(self):
        net = _staged_net()
        restored = load_network(dump_network(net))
        assert set(restored.concepts) == set(net.concepts)
        assert set(restored.predicates) == set(net.predicates)
        assert _facts_set(restored) == _facts_set(net)
        assert restored.concepts["a"].tags == frozenset({"stage"})


class TestFormulaRoundtrip:
    def test_formula_roundtrip(self):
        net = _staged_net()
        f = And((
            FactAtom("at", (net.concepts["obj"], net.concepts["a"])),
            Not(Or((FactAtom("at", (net.concepts["obj"], net.concepts["b"])),))),
        ))
        restored = formula_from_dict(formula_to_dict(f), net)
        assert formula_to_dict(restored) == formula_to_dict(f)


class TestRuleRoundtrip:
    def test_rule_roundtrip(self):
        net = _staged_net()
        rule = TransitionRule(
            name="A->B",
            guard=FactAtom("at", (net.concepts["obj"], net.concepts["a"])),
            effect=(RetractFact("at", ("obj", "a")), AddFact("at", ("obj", "b"))),
            priority=2,
            on_event="advance",
        )
        r2 = rule_from_dict(rule_to_dict(rule), net)
        assert r2.name == "A->B"
        assert r2.priority == 2
        assert r2.on_event == "advance"
        assert rule_to_dict(r2) == rule_to_dict(rule)


class TestModelRoundtrip:
    def _model(self) -> Model:
        net = _staged_net()
        obj = net.concepts["obj"]
        rules = [
            TransitionRule("A->B", FactAtom("at", (obj, net.concepts["a"])),
                           (RetractFact("at", ("obj", "a")), AddFact("at", ("obj", "b")))),
            TransitionRule("B->C", FactAtom("at", (obj, net.concepts["b"])),
                           (RetractFact("at", ("obj", "b")), AddFact("at", ("obj", "c")))),
        ]
        inv = Conditions(items=(
            Or(tuple(FactAtom("at", (obj, net.concepts[s])) for s in ("a", "b", "c"))),
        ))
        return Model(network=net, rules=rules, invariants=inv)

    def test_model_json_roundtrip_runs(self):
        model = self._model()
        restored = loads_model_json(dumps_model_json(model))
        assert len(restored.rules) == 2
        assert len(restored.invariants.items) == 1
        trace = restored.engine().run_to_fixpoint(restored.initial_state())
        assert trace.final_mode.value == "stable"
        assert trace.convergence_steps == 2

    def test_model_dump_structure(self):
        data = dump_model(self._model())
        assert set(data["transitions"].keys()) == {"rules", "invariants"}
        assert [r["name"] for r in data["transitions"]["rules"]] == ["A->B", "B->C"]

    def test_load_model_from_handwritten_doc_runs(self):
        doc = {
            "concepts": {c: {"id": c} for c in ("obj", "a", "b")},
            "predicates": {"at": {"name": "at", "arity": 2}},
            "facts": [{"predicate": "at", "args": ["obj", "a"]}],
            "transitions": {
                "rules": [{
                    "name": "A->B",
                    "guard": {"type": "FactAtom", "predicate": "at",
                              "args": [{"kind": "concept", "id": "obj"}, {"kind": "concept", "id": "a"}]},
                    "effect": [{"op": "retract", "predicate": "at", "args": ["obj", "a"]},
                               {"op": "add", "predicate": "at", "args": ["obj", "b"]}],
                }],
                "invariants": [],
            },
        }
        model = load_model(doc)
        trace = model.engine().run_to_fixpoint(model.initial_state())
        assert trace.final_mode.value == "stable"
        assert trace.convergence_steps == 1


class TestYamlRoundtrip:
    def test_yaml_roundtrip(self):
        pytest.importorskip("yaml", reason="требует extras: pip install -e '.[io]'")
        from ctmsn.io import dumps_model_yaml, loads_model_yaml
        net = _staged_net()
        obj = net.concepts["obj"]
        model = Model(
            network=net,
            rules=[TransitionRule("A->B", FactAtom("at", (obj, net.concepts["a"])),
                                  (RetractFact("at", ("obj", "a")), AddFact("at", ("obj", "b"))))],
        )
        restored = loads_model_yaml(dumps_model_yaml(model))
        assert [r.name for r in restored.rules] == ["A->B"]
        assert set(restored.network.concepts) == set(net.concepts)

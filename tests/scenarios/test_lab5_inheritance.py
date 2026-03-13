from __future__ import annotations

from ctmsn.scenarios.lab5_inheritance.model import build_network
from ctmsn.scenarios.lab5_inheritance.params import build_variables
from ctmsn.scenarios.lab5_inheritance.constraints import build_conditions
from ctmsn.scenarios.lab5_inheritance.runner import run


# ── Network structure ────────────────────────────────────────────


def test_network_concepts():
    net = build_network()
    assert len(net.concepts) == 12
    expected = {
        "animal", "bird", "fish", "penguin", "sparrow", "salmon",
        "tux", "jack", "nemo", "ability_fly", "ability_swim", "ability_breathe",
    }
    assert set(net.concepts.keys()) == expected


def test_network_predicates():
    net = build_network()
    assert len(net.predicates) == 5
    expected = {"isa", "instance_of", "has_ability", "lacks_ability", "knows_about"}
    assert set(net.predicates.keys()) == expected


def test_isa_hierarchy():
    net = build_network()
    isa_facts = list(net.facts("isa"))
    assert len(isa_facts) == 5

    tuples = {(s.args[0].id, s.args[1].id) for s in isa_facts}
    assert ("bird", "animal") in tuples
    assert ("fish", "animal") in tuples
    assert ("penguin", "bird") in tuples
    assert ("sparrow", "bird") in tuples
    assert ("salmon", "fish") in tuples


def test_instances():
    net = build_network()
    inst_facts = list(net.facts("instance_of"))
    assert len(inst_facts) == 3

    tuples = {(s.args[0].id, s.args[1].id) for s in inst_facts}
    assert ("tux", "penguin") in tuples
    assert ("jack", "sparrow") in tuples
    assert ("nemo", "salmon") in tuples


def test_abilities():
    net = build_network()
    has_facts = list(net.facts("has_ability"))
    assert len(has_facts) == 4

    lacks_facts = list(net.facts("lacks_ability"))
    assert len(lacks_facts) == 1

    lacks_tuples = {(s.args[0].id, s.args[1].id) for s in lacks_facts}
    assert ("penguin", "ability_fly") in lacks_tuples


def test_knows_about():
    net = build_network()
    knows_facts = list(net.facts("knows_about"))
    assert len(knows_facts) == 2

    tuples = {(s.args[0].id, s.args[1].id) for s in knows_facts}
    assert ("jack", "tux") in tuples
    assert ("nemo", "jack") in tuples


# ── Params & conditions ─────────────────────────────────────────


def test_variables():
    net = build_network()
    vars_, ctx0 = build_variables(net)
    assert vars_.species.name == "species"
    assert vars_.individual.name == "individual"
    assert ctx0.as_dict() == {}


def test_conditions():
    net = build_network()
    conds = build_conditions(net)
    assert len(conds.items) == 2


# ── Runner / forcing ────────────────────────────────────────────


def test_runner_check():
    out = run()
    assert out["check"].ok is False


def test_runner_check_violated():
    out = run()
    assert len(out["check"].violated) == 1


def test_runner_forces():
    out = run()
    assert out["forces"].value == "false"


def test_runner_force():
    out = run()
    assert out["result"].status.value == "false"


def test_runner_context_empty():
    out = run()
    assert out["ctx0"] == {}

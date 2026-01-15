from __future__ import annotations

from ctmsn.param.context import Context
from ctmsn.forcing.engine import ForcingEngine

from ctmsn.scenarios.fishing.model import build_network
from ctmsn.scenarios.fishing.derive import apply
from ctmsn.scenarios.fishing.constraints import build_conditions
from ctmsn.scenarios.fishing.goal import build_goal


def test_check_conditions():
    net = build_network()
    apply(net)
    
    conds = build_conditions()
    eng = ForcingEngine(net)
    ctx = Context()
    
    chk = eng.check(ctx, conds)
    assert chk.ok is True
    assert len(chk.violated) == 0
    assert len(chk.unknown) == 0


def test_forces_goal():
    net = build_network()
    apply(net)
    
    phi = build_goal()
    conds = build_conditions()
    
    eng = ForcingEngine(net)
    ctx = Context()
    
    result = eng.forces(ctx, phi, conds)
    assert result.value == "true"


def test_force_goal():
    net = build_network()
    apply(net)
    
    phi = build_goal()
    conds = build_conditions()
    
    eng = ForcingEngine(net)
    ctx = Context()
    
    result = eng.force(ctx, phi, conds)
    assert result.status.value == "true"

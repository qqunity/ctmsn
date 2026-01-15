from __future__ import annotations

from ctmsn.param.context import Context
from ctmsn.forcing.engine import ForcingEngine

from ctmsn.scenarios.spawn.model import build_network
from ctmsn.scenarios.spawn.derive import apply as derive_apply
from ctmsn.scenarios.spawn.constraints import build_conditions
from ctmsn.scenarios.spawn.goal import build_goal
from ctmsn.logic.tribool import TriBool


def test_forces_goal():
    net = build_network()
    derive_apply(net)
    
    conds = build_conditions()
    phi = build_goal()
    
    eng = ForcingEngine(net)
    ctx = Context()
    
    result = eng.forces(ctx, phi, conds)
    assert result == TriBool.TRUE


def test_force_goal():
    net = build_network()
    derive_apply(net)
    
    conds = build_conditions()
    phi = build_goal()
    
    eng = ForcingEngine(net)
    ctx = Context()
    
    result = eng.force(ctx, phi, conds)
    assert result.status.is_true()


def test_check_conditions():
    net = build_network()
    derive_apply(net)
    
    conds = build_conditions()
    
    eng = ForcingEngine(net)
    ctx = Context()
    
    chk = eng.check(ctx, conds)
    assert chk.ok is True
    assert len(chk.violated) == 0

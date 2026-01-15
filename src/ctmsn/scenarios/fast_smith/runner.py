from __future__ import annotations

from ctmsn.forcing.engine import ForcingEngine
from ctmsn.scenarios.fast_smith.model import build_network
from ctmsn.scenarios.fast_smith.params import build_variables
from ctmsn.scenarios.fast_smith.constraints import build_conditions
from ctmsn.scenarios.fast_smith.goal import build_goal


def run():
    net = build_network()
    vars_, ctx0 = build_variables(net)
    conds = build_conditions(net)
    phi = build_goal(net)

    engine = ForcingEngine(net)

    chk = engine.check(ctx0, conds)
    forces = engine.forces(ctx0, phi, conds)
    res = engine.force(ctx0, phi, conds)

    return {
        "check": chk,
        "forces": forces,
        "result": res,
        "ctx0": ctx0.as_dict(),
    }

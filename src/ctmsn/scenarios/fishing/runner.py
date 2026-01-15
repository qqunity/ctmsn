from __future__ import annotations

from ctmsn.param.context import Context
from ctmsn.forcing.engine import ForcingEngine

from ctmsn.scenarios.fishing.model import build_network
from ctmsn.scenarios.fishing.derive import apply as derive_apply
from ctmsn.scenarios.fishing.constraints import build_conditions
from ctmsn.scenarios.fishing.goal import build_goal
from ctmsn.scenarios.fishing.explain import explain_comp2, explain_compN


def run():
    net = build_network()

    deriv = derive_apply(net)

    conds = build_conditions()
    phi = build_goal()

    eng = ForcingEngine(net)
    ctx = Context()

    chk = eng.check(ctx, conds)
    forces = eng.forces(ctx, phi, conds)
    res = eng.force(ctx, phi, conds)

    expl = []
    expl += explain_comp2(net, "h", "g_minus", "s")
    expl += explain_comp2(net, "h", "g_plus", "j")
    expl += explain_comp2(net, "s", "catch", "j")
    expl += explain_compN(net, "hook+∘fake+∘eat∘sf", "catch_sf")

    return {
        "derivation": deriv,
        "check": chk,
        "forces": forces,
        "result": res,
        "explain": expl,
    }

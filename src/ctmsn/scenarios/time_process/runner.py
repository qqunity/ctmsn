from __future__ import annotations

from ctmsn.forcing.engine import ForcingEngine
from ctmsn.scenarios.time_process.model import build_network
from ctmsn.scenarios.time_process.constraints import build_conditions
from ctmsn.scenarios.time_process.goal import build_goal
from ctmsn.scenarios.time_process import derive
from ctmsn.scenarios.time_process.explain import explain_composition


def run(mode: str = "sun"):
    net = build_network(mode=mode)

    deriv_stats = derive.apply(net, mode=mode)

    conds = build_conditions(mode=mode)
    phi = build_goal(mode=mode)

    engine = ForcingEngine(net)

    engine_ctx = __empty_ctx()
    chk = engine.check(engine_ctx, conds)
    forces = engine.forces(engine_ctx, phi, conds)
    res = engine.force(engine_ctx, phi, conds)

    expl = []
    if mode == "sun":
        expl += explain_composition(net, "sun_before", "below", "sunset")
        expl += explain_composition(net, "sun_after", "above", "sunrise")
    else:
        expl += explain_composition(net, "h_before", "g_minus", "h_minus")
        expl += explain_composition(net, "h_after", "g_plus", "h_plus")

    return {
        "mode": mode,
        "derivation": deriv_stats,
        "check": chk,
        "forces": forces,
        "result": res,
        "explain": expl,
    }


def __empty_ctx():
    from ctmsn.param.context import Context
    return Context()

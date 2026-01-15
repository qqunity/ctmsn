from __future__ import annotations

from ctmsn.param.context import Context
from ctmsn.forcing.engine import ForcingEngine

from ctmsn.scenarios.spawn.model import build_network
from ctmsn.scenarios.spawn.derive import apply as derive_apply
from ctmsn.scenarios.spawn.constraints import build_conditions
from ctmsn.scenarios.spawn.goal import build_goal
from ctmsn.scenarios.spawn.explain import explain_comp2, explain_compN


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
    expl += explain_comp2(net, "fish", "not_eat", "spawner")
    expl += explain_comp2(net, "fish", "eat", "milter")
    expl += explain_comp2(net, "milter_f", "push", "spawner_f")
    expl += explain_comp2(net, "spawner_f", "rethink", "milter_f")
    expl += explain_compN(net, "rethink∘push∘milter_f", "milter_f")
    expl += explain_compN(net, "(rethink∘spawner_f)_e", "milter_fe")

    return {
        "derivation": deriv,
        "check": chk,
        "forces": forces,
        "result": res,
        "explain": expl,
    }

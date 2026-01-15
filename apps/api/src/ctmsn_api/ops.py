from __future__ import annotations
from typing import Any
import inspect
from ctmsn.param.context import Context
from ctmsn.forcing.engine import ForcingEngine

def run_ops(net, spec, derive: bool, mode: str | None = None) -> dict[str, Any]:
    derivation = None
    if derive and spec.derive_apply:
        sig = inspect.signature(spec.derive_apply)
        params = list(sig.parameters.keys())
        if len(params) > 1 and 'mode' in params:
            derivation = spec.derive_apply(net, mode or "sun")
        else:
            derivation = spec.derive_apply(net)

    eng = ForcingEngine(net)
    ctx = Context()

    out: dict[str, Any] = {"derivation": derivation}

    if spec.conditions:
        sig = inspect.signature(spec.conditions)
        params = list(sig.parameters.keys())
        if 'net' in params and 'mode' in params:
            conds = spec.conditions(net, mode or "sun")
        elif 'net' in params:
            conds = spec.conditions(net)
        elif 'mode' in params:
            conds = spec.conditions(mode or "sun")
        else:
            conds = spec.conditions()
        out["check"] = str(eng.check(ctx, conds))
    else:
        out["check"] = None

    if spec.goal and spec.conditions:
        sig_conds = inspect.signature(spec.conditions)
        params_conds = list(sig_conds.parameters.keys())
        if 'net' in params_conds and 'mode' in params_conds:
            conds = spec.conditions(net, mode or "sun")
        elif 'net' in params_conds:
            conds = spec.conditions(net)
        elif 'mode' in params_conds:
            conds = spec.conditions(mode or "sun")
        else:
            conds = spec.conditions()
        
        sig_goal = inspect.signature(spec.goal)
        params_goal = list(sig_goal.parameters.keys())
        if 'net' in params_goal and 'mode' in params_goal:
            goal = spec.goal(net, mode or "sun")
        elif 'net' in params_goal:
            goal = spec.goal(net)
        elif 'mode' in params_goal:
            goal = spec.goal(mode or "sun")
        else:
            goal = spec.goal()
        
        out["forces"] = str(eng.forces(ctx, goal, conds))
        out["force"] = str(eng.force(ctx, goal, conds))
    else:
        out["forces"] = None
        out["force"] = None

    return out

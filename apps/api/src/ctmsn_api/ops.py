from __future__ import annotations
from typing import Any
import inspect
from ctmsn.core.concept import Concept
from ctmsn.param.context import Context
from ctmsn.param.domain import EnumDomain, RangeDomain, PredicateDomain
from ctmsn.param.variable import Variable
from ctmsn.forcing.engine import ForcingEngine


def _build_context(variables_result: tuple | None, context_values: dict[str, Any] | None) -> Context:
    ctx = Context()

    if variables_result is not None and len(variables_result) >= 2:
        default_ctx = variables_result[1]
        vars_obj = variables_result[0]
        var_map: dict[str, Variable] = {}
        for attr_name in dir(vars_obj):
            val = getattr(vars_obj, attr_name, None)
            if isinstance(val, Variable):
                var_map[val.name] = val

        for k, v in default_ctx.as_dict().items():
            if k in var_map:
                ctx.set(var_map[k], v)

        if context_values:
            for k, v in context_values.items():
                if k in var_map:
                    try:
                        ctx.set(var_map[k], v)
                    except ValueError:
                        pass
                else:
                    # User-created variable: already validated in set_variable
                    ctx._values[k] = v
    elif context_values:
        # No scenario variables, but user variables may have values
        for k, v in context_values.items():
            ctx._values[k] = v

    return ctx


def get_variable_info(
    spec, net, mode: str | None = None, user_variables: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]] | None:
    result: list[dict[str, Any]] = []

    if spec.variables:
        sig = inspect.signature(spec.variables)
        params = list(sig.parameters.keys())
        try:
            if 'net' in params or len(params) >= 1:
                variables_result = spec.variables(net)
            else:
                variables_result = spec.variables()
        except KeyError:
            if user_variables:
                result.extend(user_variables)
            return result if result else None

        vars_obj = variables_result[0]
        for attr_name in dir(vars_obj):
            val = getattr(vars_obj, attr_name, None)
            if not isinstance(val, Variable):
                continue
            info: dict[str, Any] = {
                "name": val.name,
                "type_tag": val.type_tag,
                "origin": "scenario",
            }
            domain = val.domain
            if isinstance(domain, EnumDomain):
                info["domain_type"] = "enum"
                values = []
                for v in domain.values:
                    if isinstance(v, Concept):
                        values.append(v.id)
                    else:
                        values.append(str(v))
                info["values"] = values
            elif isinstance(domain, RangeDomain):
                info["domain_type"] = "range"
                info["min"] = domain.min_value
                info["max"] = domain.max_value
            elif isinstance(domain, PredicateDomain):
                info["domain_type"] = "predicate"
            else:
                info["domain_type"] = "unknown"
            result.append(info)

    if user_variables:
        result.extend(user_variables)

    return result if result else None


def _get_variables_result(spec, net):
    if not spec.variables:
        return None
    sig = inspect.signature(spec.variables)
    params = list(sig.parameters.keys())
    try:
        if 'net' in params or len(params) >= 1:
            return spec.variables(net)
        return spec.variables()
    except KeyError:
        return None


def _serialize_context(ctx: Context, net) -> dict[str, Any]:
    raw = ctx.as_dict()
    result: dict[str, Any] = {}
    for k, v in raw.items():
        if isinstance(v, Concept):
            result[k] = v.id
        else:
            result[k] = v
    return result


def run_ops(net, spec, derive: bool, mode: str | None = None, context_values: dict[str, Any] | None = None) -> dict[str, Any]:
    derivation = None
    if derive and spec.derive_apply:
        sig = inspect.signature(spec.derive_apply)
        params = list(sig.parameters.keys())
        if len(params) > 1 and 'mode' in params:
            derivation = spec.derive_apply(net, mode or "sun")
        else:
            derivation = spec.derive_apply(net)

    eng = ForcingEngine(net)

    variables_result = _get_variables_result(spec, net)
    ctx = _build_context(variables_result, context_values)

    out: dict[str, Any] = {"derivation": derivation}

    conds = None
    if spec.conditions:
        sig = inspect.signature(spec.conditions)
        params = list(sig.parameters.keys())
        try:
            if 'net' in params and 'mode' in params:
                conds = spec.conditions(net, mode or "sun")
            elif 'net' in params:
                conds = spec.conditions(net)
            elif 'mode' in params:
                conds = spec.conditions(mode or "sun")
            else:
                conds = spec.conditions()
        except KeyError:
            conds = None

    if conds is not None:
        out["check"] = str(eng.check(ctx, conds))
    else:
        out["check"] = None

    goal = None
    if spec.goal and conds is not None:
        sig_goal = inspect.signature(spec.goal)
        params_goal = list(sig_goal.parameters.keys())
        try:
            if 'net' in params_goal and 'mode' in params_goal:
                goal = spec.goal(net, mode or "sun")
            elif 'net' in params_goal:
                goal = spec.goal(net)
            elif 'mode' in params_goal:
                goal = spec.goal(mode or "sun")
            else:
                goal = spec.goal()
        except KeyError:
            goal = None

    if goal is not None and conds is not None:
        out["forces"] = str(eng.forces(ctx, goal, conds))
        out["force"] = str(eng.force(ctx, goal, conds))
    else:
        out["forces"] = None
        out["force"] = None

    out["variables"] = get_variable_info(spec, net, mode)
    out["context"] = _serialize_context(ctx, net)

    return out

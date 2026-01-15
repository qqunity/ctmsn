from __future__ import annotations
from typing import Any

from ctmsn.core.network import SemanticNetwork
from ctmsn.core.concept import Concept
from ctmsn.param.context import Context
from ctmsn.param.variable import Variable
from ctmsn.logic.tribool import TriBool
from ctmsn.logic.formula import (
    Formula, FactAtom, EqAtom, Not, And, Or, Implies
)

def _resolve_term(term: Any, ctx: Context) -> tuple[TriBool, Any]:
    if isinstance(term, Variable):
        if not ctx.is_assigned(term):
            return (TriBool.UNKNOWN, None)
        return (TriBool.TRUE, ctx.get(term))
    return (TriBool.TRUE, term)

def evaluate(formula: Formula, net: SemanticNetwork, ctx: Context) -> TriBool:
    if isinstance(formula, FactAtom):
        resolved_args = []
        for a in formula.args:
            st, v = _resolve_term(a, ctx)
            if st is TriBool.UNKNOWN:
                return TriBool.UNKNOWN
            resolved_args.append(v)

        for f in net.facts(formula.predicate):
            if len(f.args) != len(resolved_args):
                continue
            ok = True
            for fa, ra in zip(f.args, resolved_args):
                if isinstance(fa, Concept) and isinstance(ra, Concept):
                    if fa.id != ra.id:
                        ok = False; break
                else:
                    if fa != ra:
                        ok = False; break
            if ok:
                return TriBool.TRUE
        return TriBool.FALSE

    if isinstance(formula, EqAtom):
        l_s, l = _resolve_term(formula.left, ctx)
        r_s, r = _resolve_term(formula.right, ctx)
        if TriBool.UNKNOWN in (l_s, r_s):
            return TriBool.UNKNOWN
        return TriBool.TRUE if l == r else TriBool.FALSE

    if isinstance(formula, Not):
        v = evaluate(formula.inner, net, ctx)
        if v is TriBool.UNKNOWN:
            return TriBool.UNKNOWN
        return TriBool.FALSE if v is TriBool.TRUE else TriBool.TRUE

    if isinstance(formula, And):
        any_unknown = False
        for it in formula.items:
            v = evaluate(it, net, ctx)
            if v is TriBool.FALSE:
                return TriBool.FALSE
            if v is TriBool.UNKNOWN:
                any_unknown = True
        return TriBool.UNKNOWN if any_unknown else TriBool.TRUE

    if isinstance(formula, Or):
        any_unknown = False
        for it in formula.items:
            v = evaluate(it, net, ctx)
            if v is TriBool.TRUE:
                return TriBool.TRUE
            if v is TriBool.UNKNOWN:
                any_unknown = True
        return TriBool.UNKNOWN if any_unknown else TriBool.FALSE

    if isinstance(formula, Implies):
        l = evaluate(formula.left, net, ctx)
        r = evaluate(formula.right, net, ctx)
        if l is TriBool.FALSE:
            return TriBool.TRUE
        if l is TriBool.TRUE:
            return r
        if r is TriBool.TRUE:
            return TriBool.TRUE
        return TriBool.UNKNOWN

    raise TypeError(f"Unsupported formula type: {type(formula)}")

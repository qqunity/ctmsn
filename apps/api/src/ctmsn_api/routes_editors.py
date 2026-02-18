from __future__ import annotations

import json
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ctmsn.core.concept import Concept
from ctmsn.logic.evaluator import evaluate
from ctmsn.param.context import Context
from ctmsn.param.domain import EnumDomain, PredicateDomain, RangeDomain
from ctmsn.param.variable import Variable
from ctmsn_api.auth import get_current_user
from ctmsn_api.database import get_db
from ctmsn_api.formula_serde import formula_from_json, formula_to_json, formula_to_text
from ctmsn_api.models import FormulaRecord, NamedContext, User, UserVariable, Workspace
from ctmsn_api.ops import get_variable_info
from ctmsn_api.registry import get as get_spec
from ctmsn_api.sessions import context_from_json, context_to_json, get_session

router = APIRouter()


def _check_workspace(wid: str, user: User, db: Session) -> Workspace:
    ws = db.query(Workspace).filter(Workspace.id == wid).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    if ws.owner_id != user.id and user.role.value != "teacher":
        raise HTTPException(status_code=403, detail="Access denied")
    return ws


def _get_var_map(ws: Workspace, db: Session) -> dict[str, Variable]:
    st = get_session(ws.id, db)
    if not st:
        return {}
    var_map: dict[str, Variable] = {}
    spec = get_spec(st.scenario)
    if spec.variables:
        import inspect
        sig = inspect.signature(spec.variables)
        params = list(sig.parameters.keys())
        if len(params) >= 1:
            variables_result = spec.variables(st.net)
        else:
            variables_result = spec.variables()
        vars_obj = variables_result[0]
        for attr_name in dir(vars_obj):
            val = getattr(vars_obj, attr_name, None)
            if isinstance(val, Variable):
                var_map[val.name] = val

    user_vars = db.query(UserVariable).filter(UserVariable.workspace_id == ws.id).all()
    for uv in user_vars:
        domain = _build_domain(uv.domain_type, json.loads(uv.domain_json), st.net if st else None)
        var_map[uv.name] = Variable(name=uv.name, domain=domain, type_tag=uv.type_tag)

    return var_map


def _build_domain(domain_type: str, domain_data: dict, net: Optional[Any] = None) -> Any:
    if domain_type == "enum":
        raw_values = domain_data.get("values", [])
        values = []
        for v in raw_values:
            if net and v in net.concepts:
                values.append(net.concepts[v])
            else:
                values.append(v)
        return EnumDomain(values=tuple(values))
    if domain_type == "range":
        return RangeDomain(
            min_value=float(domain_data.get("min", 0)),
            max_value=float(domain_data.get("max", 100)),
            inclusive=domain_data.get("inclusive", True),
        )
    if domain_type == "predicate":
        return PredicateDomain(fn=lambda _: True, name=domain_data.get("name", "custom"))
    return PredicateDomain(fn=lambda _: True, name="any")


# ─── Formula CRUD ─────────────────────────────────────────────

class FormulaCreateReq(BaseModel):
    name: str
    formula: dict


class FormulaUpdateReq(BaseModel):
    name: Optional[str] = None
    formula: Optional[dict] = None


@router.post("/api/workspaces/{wid}/formulas")
def create_formula(
    wid: str,
    req: FormulaCreateReq,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws = _check_workspace(wid, user, db)
    rec = FormulaRecord(
        workspace_id=wid,
        name=req.name,
        formula_json=json.dumps(req.formula),
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)

    var_map = _get_var_map(ws, db)
    st = get_session(wid, db)
    text_repr = ""
    try:
        f = formula_from_json(req.formula, st.net if st else None, var_map)
        text_repr = formula_to_text(f)
    except Exception:
        text_repr = "(invalid)"

    return {
        "id": rec.id,
        "name": rec.name,
        "formula": req.formula,
        "text": text_repr,
        "created_at": rec.created_at.isoformat() if rec.created_at else None,
        "updated_at": rec.updated_at.isoformat() if rec.updated_at else None,
    }


@router.get("/api/workspaces/{wid}/formulas")
def list_formulas(
    wid: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws = _check_workspace(wid, user, db)
    records = db.query(FormulaRecord).filter(FormulaRecord.workspace_id == wid).order_by(FormulaRecord.created_at).all()
    st = get_session(wid, db)
    var_map = _get_var_map(ws, db)
    result = []
    for rec in records:
        formula_data = json.loads(rec.formula_json)
        text_repr = ""
        try:
            f = formula_from_json(formula_data, st.net if st else None, var_map)
            text_repr = formula_to_text(f)
        except Exception:
            text_repr = "(invalid)"
        result.append({
            "id": rec.id,
            "name": rec.name,
            "formula": formula_data,
            "text": text_repr,
            "created_at": rec.created_at.isoformat() if rec.created_at else None,
            "updated_at": rec.updated_at.isoformat() if rec.updated_at else None,
        })
    return {"formulas": result}


@router.put("/api/workspaces/{wid}/formulas/{fid}")
def update_formula(
    wid: str,
    fid: str,
    req: FormulaUpdateReq,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws = _check_workspace(wid, user, db)
    rec = db.query(FormulaRecord).filter(FormulaRecord.id == fid, FormulaRecord.workspace_id == wid).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Formula not found")
    if req.name is not None:
        rec.name = req.name
    if req.formula is not None:
        rec.formula_json = json.dumps(req.formula)
    db.commit()
    db.refresh(rec)

    formula_data = json.loads(rec.formula_json)
    st = get_session(wid, db)
    var_map = _get_var_map(ws, db)
    text_repr = ""
    try:
        f = formula_from_json(formula_data, st.net if st else None, var_map)
        text_repr = formula_to_text(f)
    except Exception:
        text_repr = "(invalid)"

    return {
        "id": rec.id,
        "name": rec.name,
        "formula": formula_data,
        "text": text_repr,
        "created_at": rec.created_at.isoformat() if rec.created_at else None,
        "updated_at": rec.updated_at.isoformat() if rec.updated_at else None,
    }


@router.delete("/api/workspaces/{wid}/formulas/{fid}")
def delete_formula(
    wid: str,
    fid: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _check_workspace(wid, user, db)
    rec = db.query(FormulaRecord).filter(FormulaRecord.id == fid, FormulaRecord.workspace_id == wid).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Formula not found")
    db.delete(rec)
    db.commit()
    return {"ok": True}


class FormulaEvalReq(BaseModel):
    context_id: Optional[str] = None


@router.post("/api/workspaces/{wid}/formulas/{fid}/evaluate")
def evaluate_formula(
    wid: str,
    fid: str,
    req: Optional[FormulaEvalReq] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws = _check_workspace(wid, user, db)
    rec = db.query(FormulaRecord).filter(FormulaRecord.id == fid, FormulaRecord.workspace_id == wid).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Formula not found")

    st = get_session(wid, db)
    if not st:
        raise HTTPException(status_code=400, detail="No session for workspace")

    var_map = _get_var_map(ws, db)
    formula_data = json.loads(rec.formula_json)
    formula = formula_from_json(formula_data, st.net, var_map)

    ctx_values = st.context_values
    if req and req.context_id:
        named_ctx = db.query(NamedContext).filter(
            NamedContext.id == req.context_id, NamedContext.workspace_id == wid
        ).first()
        if named_ctx:
            ctx_values = context_from_json(named_ctx.context_json, st.net)

    ctx = Context()
    for k, v in ctx_values.items():
        if k in var_map:
            try:
                ctx.set(var_map[k], v)
            except (ValueError, TypeError):
                pass

    result = evaluate(formula, st.net, ctx)
    return {"result": result.value}


# ─── Variable CRUD ────────────────────────────────────────────

class VariableCreateReq(BaseModel):
    name: str
    type_tag: Optional[str] = None
    domain_type: str  # "enum" | "range" | "predicate"
    domain: dict


class VariableUpdateReq(BaseModel):
    name: Optional[str] = None
    type_tag: Optional[str] = None
    domain_type: Optional[str] = None
    domain: Optional[dict] = None


def _serialize_user_variable(uv: UserVariable) -> dict:
    return {
        "id": uv.id,
        "name": uv.name,
        "type_tag": uv.type_tag,
        "domain_type": uv.domain_type,
        "domain": json.loads(uv.domain_json),
        "origin": "user",
        "created_at": uv.created_at.isoformat() if uv.created_at else None,
    }


@router.post("/api/workspaces/{wid}/variables")
def create_variable(
    wid: str,
    req: VariableCreateReq,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _check_workspace(wid, user, db)
    uv = UserVariable(
        workspace_id=wid,
        name=req.name,
        type_tag=req.type_tag,
        domain_type=req.domain_type,
        domain_json=json.dumps(req.domain),
    )
    db.add(uv)
    db.commit()
    db.refresh(uv)
    return _serialize_user_variable(uv)


@router.get("/api/workspaces/{wid}/variables")
def list_variables(
    wid: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws = _check_workspace(wid, user, db)
    st = get_session(wid, db)
    result: list[dict] = []

    if st:
        spec = get_spec(st.scenario)
        scenario_vars = get_variable_info(spec, st.net, st.mode)
        if scenario_vars:
            for sv in scenario_vars:
                sv["origin"] = "scenario"
                result.append(sv)

    user_vars = db.query(UserVariable).filter(UserVariable.workspace_id == wid).order_by(UserVariable.created_at).all()
    for uv in user_vars:
        result.append(_serialize_user_variable(uv))

    return {"variables": result}


@router.put("/api/workspaces/{wid}/variables/{vid}")
def update_variable(
    wid: str,
    vid: str,
    req: VariableUpdateReq,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _check_workspace(wid, user, db)
    uv = db.query(UserVariable).filter(UserVariable.id == vid, UserVariable.workspace_id == wid).first()
    if not uv:
        raise HTTPException(status_code=404, detail="Variable not found")
    if req.name is not None:
        uv.name = req.name
    if req.type_tag is not None:
        uv.type_tag = req.type_tag
    if req.domain_type is not None:
        uv.domain_type = req.domain_type
    if req.domain is not None:
        uv.domain_json = json.dumps(req.domain)
    db.commit()
    db.refresh(uv)
    return _serialize_user_variable(uv)


@router.delete("/api/workspaces/{wid}/variables/{vid}")
def delete_variable(
    wid: str,
    vid: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _check_workspace(wid, user, db)
    uv = db.query(UserVariable).filter(UserVariable.id == vid, UserVariable.workspace_id == wid).first()
    if not uv:
        raise HTTPException(status_code=404, detail="Variable not found")
    db.delete(uv)
    db.commit()
    return {"ok": True}


# ─── Context CRUD ─────────────────────────────────────────────

class ContextCreateReq(BaseModel):
    name: str
    clone_from: Optional[str] = None


class ContextUpdateReq(BaseModel):
    name: Optional[str] = None
    context: Optional[dict] = None


class SetContextVariableReq(BaseModel):
    variable: str
    value: Any


class CompareContextsReq(BaseModel):
    context_ids: list[str]


def _count_context_vars(ws: Workspace, db: Session) -> int:
    st = get_session(ws.id, db)
    count = 0
    if st:
        spec = get_spec(st.scenario)
        scenario_vars = get_variable_info(spec, st.net, st.mode)
        if scenario_vars:
            count += len(scenario_vars)
    user_vars = db.query(UserVariable).filter(UserVariable.workspace_id == ws.id).count()
    count += user_vars
    return count


def _serialize_context(nc: NamedContext, total_vars: int) -> dict:
    ctx_data = json.loads(nc.context_json) if nc.context_json else {}
    assigned = len(ctx_data)
    return {
        "id": nc.id,
        "name": nc.name,
        "context": ctx_data,
        "is_active": nc.is_active == 1,
        "is_complete": assigned >= total_vars if total_vars > 0 else True,
        "total_vars": total_vars,
        "assigned_vars": assigned,
        "created_at": nc.created_at.isoformat() if nc.created_at else None,
        "updated_at": nc.updated_at.isoformat() if nc.updated_at else None,
    }


@router.post("/api/workspaces/{wid}/contexts")
def create_context(
    wid: str,
    req: ContextCreateReq,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws = _check_workspace(wid, user, db)
    ctx_json = "{}"
    if req.clone_from:
        source = db.query(NamedContext).filter(
            NamedContext.id == req.clone_from, NamedContext.workspace_id == wid
        ).first()
        if source:
            ctx_json = source.context_json

    nc = NamedContext(workspace_id=wid, name=req.name, context_json=ctx_json)
    db.add(nc)
    db.commit()
    db.refresh(nc)
    total = _count_context_vars(ws, db)
    return _serialize_context(nc, total)


@router.get("/api/workspaces/{wid}/contexts")
def list_contexts(
    wid: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws = _check_workspace(wid, user, db)
    records = db.query(NamedContext).filter(NamedContext.workspace_id == wid).order_by(NamedContext.created_at).all()
    total = _count_context_vars(ws, db)
    return {"contexts": [_serialize_context(nc, total) for nc in records]}


@router.put("/api/workspaces/{wid}/contexts/{cid}")
def update_context(
    wid: str,
    cid: str,
    req: ContextUpdateReq,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws = _check_workspace(wid, user, db)
    nc = db.query(NamedContext).filter(NamedContext.id == cid, NamedContext.workspace_id == wid).first()
    if not nc:
        raise HTTPException(status_code=404, detail="Context not found")
    if req.name is not None:
        nc.name = req.name
    if req.context is not None:
        nc.context_json = json.dumps(req.context)
    db.commit()
    db.refresh(nc)
    total = _count_context_vars(ws, db)
    return _serialize_context(nc, total)


@router.delete("/api/workspaces/{wid}/contexts/{cid}")
def delete_context(
    wid: str,
    cid: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _check_workspace(wid, user, db)
    nc = db.query(NamedContext).filter(NamedContext.id == cid, NamedContext.workspace_id == wid).first()
    if not nc:
        raise HTTPException(status_code=404, detail="Context not found")
    db.delete(nc)
    db.commit()
    return {"ok": True}


@router.post("/api/workspaces/{wid}/contexts/{cid}/activate")
def activate_context(
    wid: str,
    cid: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws = _check_workspace(wid, user, db)
    nc = db.query(NamedContext).filter(NamedContext.id == cid, NamedContext.workspace_id == wid).first()
    if not nc:
        raise HTTPException(status_code=404, detail="Context not found")

    db.query(NamedContext).filter(NamedContext.workspace_id == wid).update({"is_active": 0})
    nc.is_active = 1

    st = get_session(wid, db)
    if st:
        ctx_values = context_from_json(nc.context_json, st.net)
        ws.context_json = context_to_json(ctx_values, st.net)

    db.commit()
    db.refresh(nc)
    total = _count_context_vars(ws, db)
    return _serialize_context(nc, total)


@router.post("/api/workspaces/{wid}/contexts/{cid}/set_variable")
def set_context_variable(
    wid: str,
    cid: str,
    req: SetContextVariableReq,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws = _check_workspace(wid, user, db)
    nc = db.query(NamedContext).filter(NamedContext.id == cid, NamedContext.workspace_id == wid).first()
    if not nc:
        raise HTTPException(status_code=404, detail="Context not found")

    ctx_data = json.loads(nc.context_json) if nc.context_json else {}
    ctx_data[req.variable] = req.value
    nc.context_json = json.dumps(ctx_data)

    if nc.is_active == 1:
        st = get_session(wid, db)
        if st:
            ctx_values = context_from_json(nc.context_json, st.net)
            ws.context_json = context_to_json(ctx_values, st.net)

    db.commit()
    db.refresh(nc)
    total = _count_context_vars(ws, db)
    return _serialize_context(nc, total)


@router.post("/api/workspaces/{wid}/contexts/compare")
def compare_contexts(
    wid: str,
    req: CompareContextsReq,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws = _check_workspace(wid, user, db)
    if len(req.context_ids) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 contexts to compare")

    total = _count_context_vars(ws, db)
    contexts_data = []
    all_vars: set[str] = set()

    for cid in req.context_ids:
        nc = db.query(NamedContext).filter(NamedContext.id == cid, NamedContext.workspace_id == wid).first()
        if not nc:
            raise HTTPException(status_code=404, detail=f"Context {cid} not found")
        ctx_dict = json.loads(nc.context_json) if nc.context_json else {}
        all_vars.update(ctx_dict.keys())
        contexts_data.append((_serialize_context(nc, total), ctx_dict))

    diff: dict[str, list] = {}
    for var_name in sorted(all_vars):
        values = [cd.get(var_name) for _, cd in contexts_data]
        if len(set(str(v) for v in values)) > 1:
            diff[var_name] = values

    return {
        "contexts": [c for c, _ in contexts_data],
        "diff": diff,
    }


@router.get("/api/workspaces/{wid}/contexts/{cid}/highlights")
def get_context_highlights(
    wid: str,
    cid: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws = _check_workspace(wid, user, db)
    nc = db.query(NamedContext).filter(NamedContext.id == cid, NamedContext.workspace_id == wid).first()
    if not nc:
        raise HTTPException(status_code=404, detail="Context not found")

    st = get_session(wid, db)
    if not st:
        return {"nodes": [], "edges": []}

    ctx_data = json.loads(nc.context_json) if nc.context_json else {}
    highlighted_nodes: set[str] = set()
    highlighted_edges: set[str] = set()

    for var_name, value in ctx_data.items():
        val_str = str(value)
        if val_str in st.net.concepts:
            highlighted_nodes.add(val_str)

    for fact in st.net.facts():
        args_ids = [a.id if isinstance(a, Concept) else str(a) for a in fact.args]
        if any(aid in highlighted_nodes for aid in args_ids):
            edge_id = f"{fact.predicate}__{'_'.join(args_ids)}"
            highlighted_edges.add(edge_id)
            for aid in args_ids:
                if aid in st.net.concepts:
                    highlighted_nodes.add(aid)

    return {
        "nodes": sorted(highlighted_nodes),
        "edges": sorted(highlighted_edges),
    }

from __future__ import annotations
import uuid
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ctmsn_api.registry import init_registry, list_specs, get as get_spec
from ctmsn_api.sessions import get_session, put_session, SessionState
from ctmsn_api.serialize import serialize
from ctmsn_api.ops import run_ops

app = FastAPI(title="CTnSS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_registry()

@app.get("/api/scenarios")
def scenarios():
    return {"scenarios": list_specs()}

@app.post("/api/session/new")
def new_session():
    return {"session_id": uuid.uuid4().hex}

class LoadReq(BaseModel):
    session_id: str
    scenario: str
    mode: Optional[str] = None
    derive: bool = True

@app.post("/api/session/load")
def load(req: LoadReq):
    spec = get_spec(req.scenario)
    net = spec.build(mode=req.mode) if req.mode else spec.build()
    put_session(req.session_id, SessionState(req.scenario, req.mode, net))

    ops = run_ops(net, spec, derive=req.derive, mode=req.mode)
    return {
        "session_id": req.session_id,
        "scenario": req.scenario,
        "mode": req.mode,
        "graph": serialize(net),
        **ops,
    }

class RunReq(BaseModel):
    session_id: str
    derive: bool = True

@app.post("/api/run")
def run(req: RunReq):
    st = get_session(req.session_id)
    if not st:
        return {"error": "unknown session"}

    spec = get_spec(st.scenario)
    ops = run_ops(st.net, spec, derive=req.derive, mode=st.mode)
    return {
        "session_id": req.session_id,
        "scenario": st.scenario,
        "mode": st.mode,
        "graph": serialize(st.net),
        **ops,
    }

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from ctmsn.core.network import SemanticNetwork

@dataclass
class SessionState:
    scenario: str
    mode: Optional[str]
    net: SemanticNetwork

_SESSIONS: dict[str, SessionState] = {}

def get_session(sid: str) -> Optional[SessionState]:
    return _SESSIONS.get(sid)

def put_session(sid: str, st: SessionState) -> None:
    _SESSIONS[sid] = st

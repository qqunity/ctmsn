from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional

from ctmsn.core.network import SemanticNetwork
from ctmsn.logic.formula import Formula
from ctmsn.forcing.conditions import Conditions

@dataclass(frozen=True)
class ScenarioSpec:
    name: str
    build: Callable[..., SemanticNetwork]
    derive_apply: Optional[Callable[..., dict]] = None
    goal: Optional[Callable[..., Formula]] = None
    conditions: Optional[Callable[..., Conditions]] = None
    modes: tuple[str, ...] = ()
    variables: Optional[Callable[..., tuple]] = None

SCENARIOS: dict[str, ScenarioSpec] = {}

def register(spec: ScenarioSpec) -> None:
    SCENARIOS[spec.name] = spec

def list_specs() -> list[dict]:
    return [{"name": s.name, "modes": list(s.modes)} for s in SCENARIOS.values()]

def get(name: str) -> ScenarioSpec:
    return SCENARIOS[name]

def init_registry() -> None:
    try:
        from ctmsn.scenarios.fishing.model import build_network as build_fish
        from ctmsn.scenarios.fishing.derive import apply as derive_fish
        from ctmsn.scenarios.fishing.goal import build_goal as goal_fish
        from ctmsn.scenarios.fishing.constraints import build_conditions as conds_fish
        register(ScenarioSpec("fishing", build_fish, derive_fish, goal_fish, conds_fish))
    except Exception:
        pass

    try:
        from ctmsn.scenarios.time_process.model import build_network as build_time
        from ctmsn.scenarios.time_process.derive import apply as derive_time
        from ctmsn.scenarios.time_process.goal import build_goal as goal_time
        from ctmsn.scenarios.time_process.constraints import build_conditions as conds_time
        register(ScenarioSpec("time_process", build_time, derive_time, goal_time, conds_time, modes=("sun", "prereq")))
    except Exception:
        pass

    try:
        from ctmsn.scenarios.spawn.model import build_network as build_spawn
        from ctmsn.scenarios.spawn.derive import apply as derive_spawn
        from ctmsn.scenarios.spawn.goal import build_goal as goal_spawn
        from ctmsn.scenarios.spawn.constraints import build_conditions as conds_spawn
        register(ScenarioSpec("spawn", build_spawn, derive_spawn, goal_spawn, conds_spawn))
    except Exception:
        pass

    try:
        from ctmsn.scenarios.fast_smith.model import build_network as build_fast
        from ctmsn.scenarios.fast_smith.goal import build_goal as goal_fast
        from ctmsn.scenarios.fast_smith.constraints import build_conditions as conds_fast
        from ctmsn.scenarios.fast_smith.params import build_variables as vars_fast
        register(ScenarioSpec("fast_smith", build_fast, None, goal_fast, conds_fast, variables=vars_fast))
    except Exception:
        pass

    try:
        from ctmsn.scenarios.lab1_university.model import build_network as build_lab1
        from ctmsn.scenarios.lab1_university.goal import build_goal as goal_lab1
        from ctmsn.scenarios.lab1_university.constraints import build_conditions as conds_lab1
        from ctmsn.scenarios.lab1_university.params import build_variables as vars_lab1
        register(ScenarioSpec("lab1_university", build_lab1, None, goal_lab1, conds_lab1, variables=vars_lab1))
    except Exception:
        pass

    try:
        from ctmsn.scenarios.lab3_formulas.model import build_network as build_lab3
        from ctmsn.scenarios.lab3_formulas.goal import build_goal as goal_lab3
        from ctmsn.scenarios.lab3_formulas.constraints import build_conditions as conds_lab3
        from ctmsn.scenarios.lab3_formulas.params import build_variables as vars_lab3
        register(ScenarioSpec("lab3_formulas", build_lab3, None, goal_lab3, conds_lab3, variables=vars_lab3))
    except Exception:
        pass

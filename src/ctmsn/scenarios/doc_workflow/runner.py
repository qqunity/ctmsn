from __future__ import annotations

from typing import Any

from ctmsn.forcing.engine import ForcingEngine
from ctmsn.io.model import dumps_model_json, loads_model_json
from ctmsn.transition import TransitionEngine, check_model, make_state
from ctmsn.experiment.runner import run_case

from ctmsn.scenarios.doc_workflow.model import build_network
from ctmsn.scenarios.doc_workflow.params import build_variables
from ctmsn.scenarios.doc_workflow.constraints import build_conditions
from ctmsn.scenarios.doc_workflow.goal import build_goal
from ctmsn.scenarios.doc_workflow.transition import build_invariants, build_rules
from ctmsn.scenarios.doc_workflow.model_doc import build_model
from ctmsn.scenarios.doc_workflow.experiment import build_case


def _final_net(net, rules, invariants):
    """Воспроизвести переходы и вернуть итоговую сеть (для пост-форсинга)."""
    engine = TransitionEngine(rules=rules, invariants=invariants, max_steps=50)
    cur = make_state(net)
    while True:
        res = engine.step(cur, None)
        if res is None:
            break
        cur, _ = res
    return cur.net


def run() -> dict[str, Any]:
    """Полный конвейер сценария: форсинг → переходы → верификация → метрики → DSL."""
    net = build_network()
    v, ctx0 = build_variables(net)
    conds = build_conditions(net)
    phi = build_goal(net)
    rules = build_rules(net)
    invariants = build_invariants(net)

    # 1. Форсинг на начальной сети: цель ещё не достижима (документ — черновик).
    eng0 = ForcingEngine(net)
    before = {
        "check": eng0.check(ctx0, conds),
        "forces": eng0.forces(ctx0, phi, conds),
        "force": eng0.force(ctx0, phi, conds),
    }

    # 2. Переходы: автономная стабилизация к устойчивому режиму.
    engine = TransitionEngine(rules=rules, invariants=invariants, max_steps=50)
    trace = engine.run_to_fixpoint(make_state(net))

    # 3. Форсинг на итоговой сети: цель достижима, reviewer подбирается.
    final_net = _final_net(net, rules, invariants)
    eng1 = ForcingEngine(final_net)
    after = {
        "forces": eng1.forces(ctx0, phi, conds),
        "force": eng1.force(ctx0, phi, conds),
    }

    # 4. Формальная верификация инвариантов по всем достижимым состояниям.
    verification = check_model(net, rules, invariants)

    # 5. Экспериментальные метрики.
    metrics = run_case(build_case()).metrics

    # 6. DSL: round-trip декларативной модели через JSON.
    model = build_model()
    restored = loads_model_json(dumps_model_json(model))
    rt_trace = restored.engine().run_to_fixpoint(restored.initial_state())
    dsl_roundtrip_ok = (
        rt_trace.final_mode == trace.final_mode
        and rt_trace.convergence_steps == trace.convergence_steps
    )

    return {
        "before": before,
        "trace": trace,
        "after": after,
        "verification": verification,
        "metrics": metrics,
        "dsl_roundtrip_ok": dsl_roundtrip_ok,
    }

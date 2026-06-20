"""Декларативное описание модели (DSL): сеть + правила переходов + инварианты.

Единый документ описывает концепты, предикаты, факты, правила переходов и
инварианты. Формат JSON поддерживается из stdlib; YAML — через опциональный
pyyaml (extras [io]). Ядро остаётся zero-dependency: pyyaml импортируется лениво.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Sequence

from ctmsn.core.network import SemanticNetwork
from ctmsn.forcing.conditions import Conditions
from ctmsn.param.context import Context
from ctmsn.transition.engine import TransitionEngine, make_state
from ctmsn.transition.rule import TransitionRule
from ctmsn.transition.state import State
from ctmsn.io.serializer import dump_context, dump_network, load_context, load_network
from ctmsn.io.transition_io import (
    invariants_from_list,
    invariants_to_list,
    rule_from_dict,
    rule_to_dict,
)


@dataclass
class Model:
    """Полная модель: семантическая сеть, правила переходов, инварианты, контекст."""

    network: SemanticNetwork
    rules: list[TransitionRule] = field(default_factory=list)
    invariants: Conditions = field(default_factory=Conditions)
    context: Context = field(default_factory=Context)

    def engine(self, max_steps: int = 100) -> TransitionEngine:
        return TransitionEngine(rules=list(self.rules), invariants=self.invariants, max_steps=max_steps)

    def initial_state(self) -> State:
        return make_state(self.network, self.context)


def dump_model(model: Model) -> dict[str, Any]:
    data = dump_network(model.network)
    data["transitions"] = {
        "rules": [rule_to_dict(r) for r in model.rules],
        "invariants": invariants_to_list(model.invariants),
    }
    ctx = dump_context(model.context)["values"]
    if ctx:
        data["context"] = ctx
    return data


def load_model(data: dict[str, Any], strict: bool = False) -> Model:
    net = load_network(data, strict=strict)
    trans = data.get("transitions", {}) or {}
    rules = [rule_from_dict(r, net) for r in trans.get("rules", [])]
    invariants = invariants_from_list(trans.get("invariants", []), net)
    context = load_context({"values": data.get("context", {})}, net)
    return Model(network=net, rules=rules, invariants=invariants, context=context)


# ─── Текстовые форматы ────────────────────────────────────────

def dumps_model_json(model: Model, indent: int = 2) -> str:
    return json.dumps(dump_model(model), ensure_ascii=False, indent=indent)


def loads_model_json(text: str, strict: bool = False) -> Model:
    return load_model(json.loads(text), strict=strict)


def _require_yaml():
    try:
        import yaml  # type: ignore
    except ImportError as e:  # pragma: no cover
        raise ImportError(
            "Поддержка YAML требует extras: pip install -e '.[io]'"
        ) from e
    return yaml


def dumps_model_yaml(model: Model) -> str:
    yaml = _require_yaml()
    return yaml.safe_dump(dump_model(model), allow_unicode=True, sort_keys=False)


def loads_model_yaml(text: str, strict: bool = False) -> Model:
    yaml = _require_yaml()
    return load_model(yaml.safe_load(text), strict=strict)


def load_model_file(path: str, strict: bool = False) -> Model:
    """Загрузить модель из файла; формат определяется по расширению (.json/.yaml/.yml)."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if path.endswith((".yaml", ".yml")):
        return loads_model_yaml(text, strict=strict)
    return loads_model_json(text, strict=strict)

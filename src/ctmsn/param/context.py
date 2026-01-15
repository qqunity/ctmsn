from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping

from ctmsn.param.variable import Variable


@dataclass
class Context:
    _values: Dict[str, Any] = field(default_factory=dict)

    def set(self, var: Variable, value: Any) -> None:
        if not var.domain.contains(value):
            raise ValueError(f"Value '{value}' not in domain of {var.name}: {var.domain.describe()}")
        self._values[var.name] = value

    def get(self, var: Variable, default: Any = None) -> Any:
        return self._values.get(var.name, default)

    def is_assigned(self, var: Variable) -> bool:
        return var.name in self._values

    def extend(self, assignments: Mapping[Variable, Any]) -> "Context":
        c = Context(_values=dict(self._values))
        for v, val in assignments.items():
            c.set(v, val)
        return c

    def as_dict(self) -> Dict[str, Any]:
        return dict(self._values)

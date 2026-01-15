from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Mapping, FrozenSet


@dataclass(frozen=True)
class Concept:
    id: str
    label: str | None = None
    tags: FrozenSet[str] = field(default_factory=frozenset)
    meta: Mapping[str, Any] = field(default_factory=dict)

    def __hash__(self) -> int:
        return hash(self.id)

    def with_tag(self, *tags: str) -> "Concept":
        return Concept(
            id=self.id,
            label=self.label,
            tags=frozenset(set(self.tags).union(tags)),
            meta=self.meta,
        )

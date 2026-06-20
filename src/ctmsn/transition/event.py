from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class Event:
    """Внешнее событие, инициирующее переход.

    name — имя события (сопоставляется с TransitionRule.on_event).
    payload — полезная нагрузка (например, привязка концептов или значений).
    """

    name: str
    payload: Mapping[str, Any] = field(default_factory=dict)

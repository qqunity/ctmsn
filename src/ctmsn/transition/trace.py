from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from ctmsn.transition.state import StateMode


@dataclass(frozen=True)
class TransitionStep:
    """Один зафиксированный шаг перехода.

    index — номер шага (от 0).
    rule — имя сработавшего правила.
    event — имя инициировавшего события (или None для автономного шага).
    added / removed — человекочитаемые описания добавленных/убранных фактов.
    invariants_ok — выполнены ли инварианты после шага.
    violated — список нарушенных инвариантов.
    mode — режим состояния после шага.
    """

    index: int
    rule: str
    event: str | None
    added: Tuple[str, ...]
    removed: Tuple[str, ...]
    invariants_ok: bool
    violated: Tuple[str, ...]
    mode: StateMode
    touched: Tuple[str, ...] = ()


@dataclass(frozen=True)
class Trace:
    """Трасса прогона: шаги, итоговый режим и метрика сходимости.

    convergence_steps — число шагов до достижения устойчивого режима;
    None, если устойчивость не достигнута (тупик, цикл или лимит шагов).
    """

    steps: Tuple[TransitionStep, ...]
    final_mode: StateMode
    convergence_steps: int | None

    def __str__(self) -> str:
        lines: list[str] = []
        for s in self.steps:
            badge = "OK" if s.invariants_ok else "НАРУШЕН ИНВАРИАНТ"
            change = []
            if s.added:
                change.append("+ " + ", ".join(s.added))
            if s.removed:
                change.append("- " + ", ".join(s.removed))
            change_str = "; ".join(change) if change else "(без изменений)"
            ev = f" [событие: {s.event}]" if s.event else ""
            lines.append(
                f"шаг {s.index}: правило '{s.rule}'{ev} -> {change_str} "
                f"[{s.mode.value}, инварианты: {badge}]"
            )
        if self.final_mode is StateMode.STABLE:
            lines.append(
                f"ИТОГ: устойчивый режим достигнут за {self.convergence_steps} шаг(ов)"
            )
        else:
            lines.append("ИТОГ: переходный режим (устойчивость не достигнута)")
        return "\n".join(lines)

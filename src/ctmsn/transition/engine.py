from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Sequence, Tuple

from ctmsn.core.concept import Concept
from ctmsn.core.statement import Statement
from ctmsn.forcing.conditions import Conditions
from ctmsn.forcing.engine import ForcingEngine
from ctmsn.transition.event import Event
from ctmsn.transition.rule import TransitionRule
from ctmsn.transition.state import State, StateMode, copy_context, make_state
from ctmsn.transition.trace import Trace, TransitionStep


def _fmt(st: Statement) -> str:
    args = ", ".join(a.id if isinstance(a, Concept) else str(a) for a in st.args)
    return f"{st.predicate}({args})"


def _concept_ids(facts) -> set[str]:
    ids: set[str] = set()
    for st in facts:
        for a in st.args:
            if isinstance(a, Concept):
                ids.add(a.id)
    return ids


@dataclass
class TransitionEngine:
    """Движок переходов: применяет правила к состоянию и строит трассу.

    rules — набор правил перехода.
    invariants — инварианты стабилизации (Conditions); проверяются на каждом шаге.
    max_steps — лимит шагов автономной стабилизации (защита от циклов/тупиков).
    """

    rules: Sequence[TransitionRule]
    invariants: Conditions = field(default_factory=Conditions)
    max_steps: int = 100

    def _ordered(self) -> list[TransitionRule]:
        return sorted(self.rules, key=lambda r: r.priority, reverse=True)

    def _first_applicable(
        self, net, context, event: Event | None
    ) -> Optional[TransitionRule]:
        for r in self._ordered():
            if r.applies(net, context, event):
                return r
        return None

    def _classify(self, net, context) -> StateMode:
        chk = ForcingEngine(net).check(context, self.invariants)
        stuck = self._first_applicable(net, context, None) is not None
        if chk.ok and not stuck:
            return StateMode.STABLE
        return StateMode.TRANSIENT

    def step(
        self, state: State, event: Event | None = None
    ) -> Optional[Tuple[State, TransitionStep]]:
        """Выполнить один переход.

        Возвращает (новое_состояние, шаг) либо None, если нет применимого
        правила или правило не меняет конфигурацию (неподвижная точка).
        """
        rule = self._first_applicable(state.net, state.context, event)
        if rule is None:
            return None

        new_net = state.net.copy()
        before = set(new_net.facts())
        rule.apply(new_net)
        after = set(new_net.facts())

        added_facts = after - before
        removed_facts = before - after
        if not added_facts and not removed_facts:
            # Гвард истинен, но эффект ничего не изменил — неподвижная точка.
            return None

        chk = ForcingEngine(new_net).check(state.context, self.invariants)
        new_context = copy_context(state.context)
        stuck = self._first_applicable(new_net, new_context, None) is not None
        mode = StateMode.STABLE if (chk.ok and not stuck) else StateMode.TRANSIENT

        new_state = State(
            net=new_net,
            context=new_context,
            index=state.index + 1,
            mode=mode,
        )
        step_rec = TransitionStep(
            index=state.index,
            rule=rule.name,
            event=event.name if event else None,
            added=tuple(sorted(_fmt(s) for s in added_facts)),
            removed=tuple(sorted(_fmt(s) for s in removed_facts)),
            invariants_ok=chk.ok,
            violated=tuple(chk.violated),
            mode=mode,
            touched=tuple(sorted(_concept_ids(added_facts) | _concept_ids(removed_facts))),
        )
        return new_state, step_rec

    def run_to_fixpoint(
        self, state: State, max_steps: int | None = None
    ) -> Trace:
        """Применять автономные правила до устойчивого режима или лимита шагов."""
        limit = max_steps if max_steps is not None else self.max_steps
        steps: list[TransitionStep] = []
        cur = state
        for _ in range(limit):
            result = self.step(cur, None)
            if result is None:
                break
            cur, rec = result
            steps.append(rec)

        final_mode = self._classify(cur.net, cur.context)
        convergence = len(steps) if final_mode is StateMode.STABLE else None
        return Trace(
            steps=tuple(steps),
            final_mode=final_mode,
            convergence_steps=convergence,
        )


__all__ = ["TransitionEngine", "make_state"]

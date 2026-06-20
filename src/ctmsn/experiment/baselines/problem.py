from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Problem:
    """Экземпляр задачи ступенчатого процесса для сравнения условий A/B/C.

    Объект должен пройти стадии s0 -> s1 -> ... -> s{n-1}, находясь в каждый
    момент ровно на одной стадии (денотационный инвариант согласованности).

    faulty=True вносит дефект: переход с индексом fault_at «теряет» объект
    (снимает текущую стадию, не добавляя следующую) — нарушение инварианта.
    Условие с денотационным слоем (C) обязано его обнаружить; baseline без
    такого слоя (A, B) пропустит дефект и завершится в несогласованном состоянии.
    """

    id: int
    n_stages: int
    faulty: bool
    fault_at: int = 0

    def stages(self) -> list[str]:
        return [f"s{i}" for i in range(self.n_stages)]


def generate_problems(
    count: int,
    *,
    fault_ratio: float = 0.5,
    n_stages: int = 4,
    seed: int = 0,
) -> list[Problem]:
    """Сгенерировать детерминированный набор задач.

    Каждая fault_ratio-я задача (по детерминированному правилу) — дефектная.
    Детерминизм обеспечивается без ГСЧ: дефектность определяется индексом.
    """
    if not (0.0 <= fault_ratio <= 1.0):
        raise ValueError("fault_ratio must be in [0, 1]")
    problems: list[Problem] = []
    threshold = fault_ratio
    for i in range(count):
        # Детерминированное чередование: доля дефектных ≈ fault_ratio.
        faulty = ((i * 1.0 + 0.5) / count) < threshold if count > 0 else False
        fault_at = (i % max(1, n_stages - 1))
        problems.append(
            Problem(id=i + seed * 1000, n_stages=n_stages, faulty=faulty, fault_at=fault_at)
        )
    return problems

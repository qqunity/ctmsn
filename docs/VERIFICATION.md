# Формальная верификация переходной системы (S5)

Документ описывает формальную проверку переходных и устойчивых режимов
(модуль `src/ctmsn/transition/`). Верификация ведётся на двух уровнях:

1. **Формальный эталон** — спецификация на TLA+ (`specs/Transition.tla`),
   проверяемая модель-чекером TLC (safety- и liveness-свойства).
2. **Воспроизводимая проверка в CI** — ограниченный model-checker на Python
   (`src/ctmsn/transition/model_check.py`), исчерпывающе обходящий достижимые
   состояния без внешних инструментов (Java/TLC не требуются).

## Соответствие «код ↔ спецификация»

| Код (`transition/`) | TLA+ (`Transition.tla`) | Python-checker |
|---|---|---|
| Факты `at(obj, s_i)` в `SemanticNetwork` | переменная `at` (множество стадий) | ключ состояния = множество фактов |
| `make_state(net, ctx)` (объект на `s0`) | `Init == at = {0}` | стартовое состояние BFS |
| `TransitionRule s_i->s_{i+1}` (retract+add) | `Advance(i)` | применение правила к копии сети |
| `ForcingEngine.check` по `Conditions` | инвариант `Consistency` | проверка инвариантов в каждом состоянии |
| `StateMode.STABLE` (неподвижная точка) | `<>(at = {N-1})` (`Termination`) | тупиковые состояния без нарушений |
| Дефект (leaky-правило) | `Faulty = TRUE` | `Problem(faulty=True)` |

### Замечание о силе инварианта

Язык формул ядра не содержит кванторов/счёта, поэтому денотационный инвариант
выражается как `Or(at(obj, s_i))` — «объект хотя бы на одной стадии». TLA+
формулирует более сильное `Consistency == Cardinality(at) = 1` — «ровно на
одной стадии». Моделируемый дефект (потеря объекта) нарушает оба инварианта,
поэтому обнаруживается на обоих уровнях. Усиление инварианта ядра до «ровно
одной» — отдельная задача расширения языка формул.

## Свойства

- **TypeOK** (safety) — типовая корректность: `at ⊆ Stages`.
- **Consistency** (safety) — денотационная согласованность состояния.
- **Termination** (liveness) — сходимость к устойчивому режиму (финальная стадия)
  при справедливости `WF_at(Next)`.

## Запуск TLC (опционально)

Требуются Java и `tla2tools.jar`
([releases](https://github.com/tlaplus/tlaplus/releases)).

```bash
# корректная конфигурация — все свойства выполняются
TLA_TOOLS=/path/to/tla2tools.jar specs/check.sh

# дефектная конфигурация — TLC находит нарушение Consistency (ожидаемо)
TLA_TOOLS=/path/to/tla2tools.jar specs/check.sh Transition_leaky.cfg
```

Без Java/TLC скрипт корректно завершается с подсказкой и не ломает CI.

## Запуск Python-checker (в CI)

Воспроизводит проверку инвариантов по всем достижимым состояниям:

```bash
python3 src/ctmsn/examples/verify_demo.py
python3 -m pytest tests/test_spec_conformance.py
```

Ожидаемый результат демо:

```
[корректная] инвариант=ДЕРЖИТСЯ, состояний=4, тупиков=1
[дефектная]  инвариант=НАРУШЕН, состояний=2, тупиков=0
    контрпример (путь правил): s0->s1
```

Программно:

```python
from ctmsn.transition import check_model
res = check_model(net, rules, invariants)
# res.invariant_holds, res.counterexample, res.states_explored
```

`check_model` из каждого состояния применяет КАЖДОЕ применимое правило (полный
обход недетерминизма порядка), что строже одношагового выбора движка; BFS даёт
кратчайший контрпример. Лимит `max_states` защищает от взрыва пространства
состояний; при его достижении выставляется флаг `truncated`.

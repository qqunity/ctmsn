# Руководство по использованию CTMSN

> **Навигация:** [🏠 Главная](README.md) | **Вы здесь: Руководство пользователя** | [Архитектура форсинга →](FORCING_IMPLEMENTATION.md)

Практическое руководство по библиотеке CTMSN: от минимального запуска до сценариев и типовых шаблонов использования.

## 📖 Содержание
- [Быстрый старт](#быстрый-старт)
- [Базовый пример](#базовый-пример)
- [Ключевые API](#ключевые-api)
- [Сценарии](#сценарии)
- [Лабораторные работы](#лабораторные-работы)
- [Запуск локального UI](#запуск-локального-ui)
- [Тестирование](#тестирование)
- [Практические рекомендации](#практические-рекомендации)

## Быстрый старт

```bash
pip3 install -e .
python3 src/ctmsn/examples/hello_forcing.py
```

Дополнительные демо:

```bash
python3 src/ctmsn/examples/fast_smith_demo.py
python3 src/ctmsn/examples/time_process_demo.py
python3 src/ctmsn/examples/fishing_demo.py
python3 src/ctmsn/examples/spawn_demo.py
python3 src/ctmsn/examples/example_usage.py
```

## Базовый пример

```python
from ctmsn.core.concept import Concept
from ctmsn.core.network import SemanticNetwork
from ctmsn.core.predicate import Predicate
from ctmsn.forcing.conditions import Conditions
from ctmsn.forcing.engine import ForcingEngine
from ctmsn.logic.formula import FactAtom
from ctmsn.logic.tribool import TriBool
from ctmsn.param.context import Context

net = SemanticNetwork()
alice = Concept("alice", "Alice")
bob = Concept("bob", "Bob")
net.add_concept(alice)
net.add_concept(bob)
net.add_predicate(Predicate("knows", 2))
net.assert_fact("knows", (alice, bob))

ctx = Context()
phi = FactAtom("knows", (alice, bob))
engine = ForcingEngine(net)

check = engine.check(ctx, Conditions())
value = engine.forces(ctx, phi, Conditions())

if check.ok and value == TriBool.TRUE:
    print("Формула форсируется")
```

## Ключевые API

### `SemanticNetwork`
- Добавление концептов: `add_concept()`
- Добавление предикатов: `add_predicate()`
- Добавление фактов: `assert_fact()`
- Проверка корректности модели: `validate()`

### `Context` и `Variable`
- Переменные: `Variable("x", domain)`
- Частичное присваивание: `ctx.set(variable, value)`
- Контекст допускает неполные назначения

### `ForcingEngine`
- `check(ctx, conditions)` — проверка ограничений
- `forces(ctx, phi, conditions)` — вычисление `TriBool`
- `force(ctx, phi, conditions, strategy)` — поиск расширения контекста для форсирования формулы

### `BruteEnumStrategy`
- Стратегия полного перебора для `force()`
- Перебирает декартово произведение доменов неприсвоенных переменных
- `max_branch=2000` — лимит пространства поиска
- Переменные с `PredicateDomain` пропускаются (домен не перечислим)

### `TriBool`
- `TriBool.TRUE`
- `TriBool.FALSE`
- `TriBool.UNKNOWN`

Используйте только явные сравнения:

```python
if result == TriBool.TRUE:
    ...
elif result == TriBool.FALSE:
    ...
else:
    ...
```

## Сценарии

Реализованные сценарии:
- `fast_smith`
- `time_process`
- `fishing`
- `spawn`
- `lab1_university`
- `lab3_formulas`

Примеры запуска:

```bash
python3 src/ctmsn/examples/fast_smith_demo.py
python3 src/ctmsn/examples/time_process_demo.py
python3 src/ctmsn/examples/fishing_demo.py
python3 src/ctmsn/examples/spawn_demo.py
```

Связанные документы:
- [FAST_SMITH_IMPLEMENTATION.md](FAST_SMITH_IMPLEMENTATION.md)
- [TIME_PROCESS_IMPLEMENTATION.md](TIME_PROCESS_IMPLEMENTATION.md)
- [FISHING_IMPLEMENTATION.md](FISHING_IMPLEMENTATION.md)
- [SPAWN_IMPLEMENTATION.md](SPAWN_IMPLEMENTATION.md)
- [Руководство по сценариям](src/ctmsn/scenarios/README.md)

## Лабораторные работы

Инструкции к лабораторным работам:
- [ЛР 1: Построение семантической сети](docs/LAB1_UNIVERSITY_INSTRUCTION.md)
- [ЛР 2: Анализ сценариев](docs/LAB2_SCENARIOS_INSTRUCTION.md)
- [ЛР 3: Формулы и трёхзначная логика](docs/LAB3_FORMULAS_INSTRUCTION.md)
- [ЛР 4: Параметризация, условия, форсинг](docs/LAB4_FORCING_INSTRUCTION.md)

## Запуск локального UI

```bash
source venv/bin/activate
make install
make dev
```

Полезные команды:

```bash
make dev-api
make dev-web
make create-teacher USERNAME=teacher PASSWORD=secret
make clean
```

## Тестирование

Ядро и сценарии:

```bash
python3 tests/test_smoke_imports.py
python3 tests/test_fast_smith.py
python3 tests/test_force_search.py
python3 -m pytest tests/scenarios/test_spawn_builds.py
python3 -m pytest tests/scenarios/test_time_process_derivation.py
```

UI end-to-end:

```bash
source venv/bin/activate
make test-e2e
```

## Практические рекомендации

- Сначала вызывайте `check()`, затем `forces()` и только после этого `force()`
- Везде обрабатывайте три состояния `TriBool`
- Помните, что `Conditions.add()` возвращает новый объект
- Используйте сценарии как шаблоны для собственных задач
- Для UI изменений покрывайте изменения e2e-тестами

---

> **См. также:**
> - [README.md](README.md)
> - [FORCING_IMPLEMENTATION.md](FORCING_IMPLEMENTATION.md)
> - [src/ctmsn/scenarios/README.md](src/ctmsn/scenarios/README.md)

> **Навигация:** [🏠 Главная](README.md) | **Вы здесь: Руководство пользователя** | [Архитектура форсинга →](FORCING_IMPLEMENTATION.md)

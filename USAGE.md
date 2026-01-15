# Руководство по использованию CTMSN

> **Навигация:** [🏠 Главная](README.md) | **Вы здесь: Руководство пользователя** | [Следующее: Архитектура форсинга →](FORCING_IMPLEMENTATION.md)

---

Подробное руководство по работе с библиотекой CTMSN для семантических сетей и форсинга.

## 📖 Содержание руководства

- [Быстрый старт](#быстрый-старт)
- [Структура проекта](#структура-проекта)
- [Основные концепции](#основные-концепции)
- [Примеры использования](#примеры-использования)
- [Работа со сложными формулами](#работа-со-сложными-формулами)
- [Лучшие практики](#лучшие-практики)
- [Готовые сценарии](#готовые-сценарии)

---

## Быстрый старт

### 1. Установка

```bash
# Активация виртуального окружения (если используется)
source venv/bin/activate

# Установка в режиме разработки
pip3 install -e .
```

### 2. Запуск примеров

```bash
# Минимальный пример форсинга
python src/ctmsn/examples/hello_forcing.py

# Задача о быстром Смите
python src/ctmsn/examples/fast_smith_demo.py

# Расширенный пример (если есть)
python src/ctmsn/examples/example_usage.py
```

### 3. Запуск тестов

```bash
# Базовые тесты импортов
python tests/test_smoke_imports.py

# Тесты Fast Smith
python tests/test_fast_smith.py
```

## Структура проекта

```
src/ctmsn/
├── core/          # Ядро семантической сети
│   ├── concept.py       # Концепты
│   ├── predicate.py     # Предикаты
│   ├── statement.py     # Факты
│   └── network.py       # Семантическая сеть
├── param/         # Параметризация
│   ├── domain.py        # Домены значений
│   ├── variable.py      # Переменные
│   └── context.py       # Контексты
├── logic/         # Логический слой
│   ├── formula.py       # Формулы
│   ├── evaluator.py     # Вычисление истинности
│   ├── tribool.py       # Трёхзначная логика
│   └── terms.py         # Термы
├── forcing/       # Форсинг-движок
│   ├── engine.py        # Основной движок
│   ├── conditions.py    # Условия
│   ├── result.py        # Результаты
│   └── strategy.py      # Стратегии поиска
├── scenarios/     # Готовые сценарии
│   └── fast_smith/      # Задача о быстром Смите
├── examples/      # Примеры использования
└── io/            # Сериализация
```

## Основные концепции

### Семантическая сеть

Создание сети с концептами и отношениями:

```python
from ctmsn.core.concept import Concept
from ctmsn.core.predicate import Predicate
from ctmsn.core.network import SemanticNetwork

net = SemanticNetwork()

# Создаём концепты
alice = Concept("alice", "Alice")
bob = Concept("bob", "Bob")
net.add_concept(alice)
net.add_concept(bob)

# Создаём предикат
net.add_predicate(Predicate(name="knows", arity=2))

# Добавляем факт
net.assert_fact("knows", (alice, bob))
```

### Параметризация

Работа с переменными и доменами:

```python
from ctmsn.param.domain import EnumDomain
from ctmsn.param.variable import Variable
from ctmsn.param.context import Context

# Домен значений
domain = EnumDomain((alice, bob))

# Переменные
x = Variable("x", domain)
y = Variable("y", domain)

# Контекст (частичная интерпретация)
ctx = Context()
ctx.set(x, alice)
ctx.set(y, bob)
```

### Логические формулы

```python
from ctmsn.logic.formula import FactAtom, Not, And, Or

# Атомарная формула
phi = FactAtom("knows", (x, y))

# Сложные формулы
complex_phi = And((
    FactAtom("knows", (x, y)),
    Not(FactAtom("blocked", (x, y)))
))
```

### Форсинг

Проверка истинности и расширение контекста:

```python
from ctmsn.forcing.engine import ForcingEngine
from ctmsn.forcing.conditions import Conditions
from ctmsn.logic.tribool import TriBool

engine = ForcingEngine(net)

# 1. Проверка условий
conditions = Conditions().add(
    FactAtom("valid_user", (x,)),
    Not(FactAtom("banned", (x,)))
)

check = engine.check(ctx, conditions)
print(f"OK: {check.ok}")
print(f"Violated: {check.violated}")
print(f"Unknown: {check.unknown}")

# 2. Проверка форсирования
phi = FactAtom("knows", (x, y))
result = engine.forces(ctx, phi, conditions)

if result == TriBool.TRUE:
    print("Формула форсируется контекстом")
elif result == TriBool.FALSE:
    print("Формула не может быть истинной")
else:  # TriBool.UNKNOWN
    print("Недостаточно информации")

# 3. Попытка расширить контекст
force_result = engine.force(ctx, phi, conditions)
print(f"Статус: {force_result.status.value}")
print(f"Пояснение: {force_result.explanation}")
if force_result.context:
    print(f"Расширенный контекст: {force_result.context.as_dict()}")
```

## Примеры использования

### Пример 1: Проверка доступа пользователя

```python
from ctmsn.core.concept import Concept
from ctmsn.core.predicate import Predicate
from ctmsn.core.network import SemanticNetwork
from ctmsn.param.domain import EnumDomain
from ctmsn.param.variable import Variable
from ctmsn.param.context import Context
from ctmsn.logic.formula import FactAtom, And, Not
from ctmsn.forcing.engine import ForcingEngine
from ctmsn.forcing.conditions import Conditions
from ctmsn.logic.tribool import TriBool

# 1. Создание семантической сети
net = SemanticNetwork()

# Концепты
alice = Concept("alice", "Alice")
bob = Concept("bob", "Bob")
document = Concept("doc1", "Document 1")

net.add_concept(alice)
net.add_concept(bob)
net.add_concept(document)

# Предикаты
net.add_predicate(Predicate("registered", 1))
net.add_predicate(Predicate("banned", 1))
net.add_predicate(Predicate("can_read", 2))

# Факты
net.assert_fact("registered", (alice,))
net.assert_fact("banned", (bob,))
net.assert_fact("can_read", (alice, document))

# 2. Параметризация
users = (alice, bob)
user_var = Variable("user", EnumDomain(users))
doc_var = Variable("doc", EnumDomain((document,)))

# 3. Условия: пользователь должен быть зарегистрирован и не забанен
conditions = Conditions().add(
    FactAtom("registered", (user_var,)),
    Not(FactAtom("banned", (user_var,)))
)

# 4. Форсинг
engine = ForcingEngine(net)

# Проверка для Alice
ctx_alice = Context()
ctx_alice.set(user_var, alice)
ctx_alice.set(doc_var, document)

check = engine.check(ctx_alice, conditions)
print(f"Alice - условия OK: {check.ok}")  # True

phi = FactAtom("can_read", (user_var, doc_var))
result = engine.forces(ctx_alice, phi, conditions)
print(f"Alice может читать: {result == TriBool.TRUE}")  # True

# Проверка для Bob
ctx_bob = Context()
ctx_bob.set(user_var, bob)
ctx_bob.set(doc_var, document)

check = engine.check(ctx_bob, conditions)
print(f"Bob - условия OK: {check.ok}")  # False (banned)
print(f"Нарушено: {check.violated}")  # ['cond[1]']
```

### Пример 2: Композиция правил

```python
# Создание сети с правилами импликации
net = SemanticNetwork()

alice = Concept("alice", "Alice")
premium_service = Concept("premium", "Premium Service")

net.add_concept(alice)
net.add_concept(premium_service)

net.add_predicate(Predicate("has_subscription", 2))
net.add_predicate(Predicate("can_access", 2))

# Факты
net.assert_fact("has_subscription", (alice, premium_service))
net.assert_fact("can_access", (alice, premium_service))

# Правило: если есть подписка, то есть доступ
from ctmsn.logic.formula import Implies

rule = Implies(
    FactAtom("has_subscription", (user_var, service_var)),
    FactAtom("can_access", (user_var, service_var))
)

# Проверка правила
engine = ForcingEngine(net)
ctx = Context()
ctx.set(user_var, alice)
ctx.set(service_var, premium_service)

result = engine.forces(ctx, rule, Conditions())
print(f"Правило выполняется: {result == TriBool.TRUE}")  # True
```

### Пример 3: Работа с неопределённостью

```python
net = SemanticNetwork()

alice = Concept("alice", "Alice")
bob = Concept("bob", "Bob")
charlie = Concept("charlie", "Charlie")

for c in (alice, bob, charlie):
    net.add_concept(c)

net.add_predicate(Predicate("friend", 2))
net.assert_fact("friend", (alice, bob))
# Про Charlie ничего не известно

# Переменная с тремя вариантами
person = Variable("person", EnumDomain((alice, bob, charlie)))

# Проверка без присваивания переменной
ctx_empty = Context()
phi = FactAtom("friend", (alice, person))

engine = ForcingEngine(net)
result = engine.forces(ctx_empty, phi, Conditions())
print(f"Результат без присваивания: {result.value}")  # unknown

# Проверка с присваиванием Bob
ctx_bob = Context()
ctx_bob.set(person, bob)
result = engine.forces(ctx_bob, phi, Conditions())
print(f"Alice друг Bob: {result == TriBool.TRUE}")  # True

# Проверка с присваиванием Charlie
ctx_charlie = Context()
ctx_charlie.set(person, charlie)
result = engine.forces(ctx_charlie, phi, Conditions())
print(f"Alice друг Charlie: {result == TriBool.FALSE}")  # False
```

## Сценарии работы форсинга

### Case 1: Формула уже истинна

```python
# Контекст полностью определён, все переменные присвоены
# Формула phi истинна в семантической сети
# forces() → TriBool.TRUE
# force() → ForceResult(status=TRUE, context=ctx, explanation="Already forced")

ctx = Context()
ctx.set(x, alice)
ctx.set(y, bob)

# Факт knows(alice, bob) есть в сети
phi = FactAtom("knows", (x, y))

result = engine.force(ctx, phi, Conditions())
# result.status == TriBool.TRUE
# result.context == ctx (тот же контекст)
# result.explanation == "Already forced"
```

### Case 2: Формула неопределена

```python
# Контекст неполный — не все переменные присвоены
# Истинность phi зависит от неприсвоенных переменных
# forces() → TriBool.UNKNOWN
# force() → ForceResult(status=UNKNOWN, context=None, explanation="Search not implemented yet")

ctx = Context()
ctx.set(x, alice)
# y не присвоена!

phi = FactAtom("knows", (x, y))

result = engine.force(ctx, phi, Conditions())
# result.status == TriBool.UNKNOWN
# result.context == None (поиск не реализован)
# result.explanation == "Search not implemented yet"
```

### Case 3: Условия нарушены

```python
# Условия не выполняются в контексте
# forces() → TriBool.FALSE
# force() → ForceResult(status=FALSE, context=None, explanation="Conditions or phi are false")

ctx = Context()
ctx.set(user, bob)

conditions = Conditions().add(
    Not(FactAtom("banned", (user,)))
)

# Но bob забанен!
net.assert_fact("banned", (bob,))

phi = FactAtom("can_access", (user, resource))

result = engine.force(ctx, phi, conditions)
# result.status == TriBool.FALSE
# result.context == None
# result.explanation == "Conditions or phi are false"
```

### Case 4: Формула ложна

```python
# Формула phi определённо ложна в контексте
# (нет соответствующего факта в сети)
# forces() → TriBool.FALSE
# force() → ForceResult(status=FALSE, context=None, explanation="Conditions or phi are false")

ctx = Context()
ctx.set(x, alice)
ctx.set(y, charlie)

# Факта knows(alice, charlie) НЕТ в сети
phi = FactAtom("knows", (x, y))

result = engine.force(ctx, phi, Conditions())
# result.status == TriBool.FALSE
# result.context == None
```

## Работа со сложными формулами

### Конъюнкция (And)

```python
from ctmsn.logic.formula import And

# Пользователь должен быть взрослым И верифицированным
phi = And((
    FactAtom("adult", (user,)),
    FactAtom("verified", (user,))
))

# And возвращает TRUE только если ВСЕ конъюнкты TRUE
# Если хотя бы один FALSE → результат FALSE
# Если есть UNKNOWN и нет FALSE → результат UNKNOWN
```

### Дизъюнкция (Or)

```python
from ctmsn.logic.formula import Or

# Пользователь может быть администратором ИЛИ модератором
phi = Or((
    FactAtom("admin", (user,)),
    FactAtom("moderator", (user,))
))

# Or возвращает TRUE если ХОТЯ БЫ ОДИН дизъюнкт TRUE
# Если все FALSE → результат FALSE
# Если есть UNKNOWN и нет TRUE → результат UNKNOWN
```

### Импликация (Implies)

```python
from ctmsn.logic.formula import Implies

# Если пользователь премиум, то он может скачивать
rule = Implies(
    FactAtom("premium", (user,)),
    FactAtom("can_download", (user,))
)

# Импликация A → B:
# - Если A = FALSE → TRUE (вакуумная истинность)
# - Если A = TRUE → возвращает значение B
# - Если B = TRUE → TRUE (независимо от A)
# - Иначе → UNKNOWN
```

### Отрицание (Not)

```python
from ctmsn.logic.formula import Not

# Пользователь не забанен
phi = Not(FactAtom("banned", (user,)))

# Not инвертирует значение:
# - NOT(TRUE) = FALSE
# - NOT(FALSE) = TRUE
# - NOT(UNKNOWN) = UNKNOWN
```

### Равенство (EqAtom)

```python
from ctmsn.logic.formula import EqAtom

# Проверка, что две переменные равны
phi = EqAtom(user1, user2)

# Возвращает TRUE если значения равны
# Возвращает FALSE если значения различны
# Возвращает UNKNOWN если хотя бы одна переменная не присвоена
```

### Композиция формул

```python
# Сложные правила доступа
phi = And((
    Or((
        FactAtom("owner", (user, resource)),
        FactAtom("admin", (user,))
    )),
    Not(FactAtom("banned", (user,))),
    Implies(
        FactAtom("sensitive", (resource,)),
        FactAtom("verified", (user,))
    )
))

# Читается как:
# (пользователь владелец ИЛИ администратор)
# И (пользователь не забанен)
# И (если ресурс чувствительный, то пользователь верифицирован)
```

## Лучшие практики

### 1. Всегда проверяйте условия перед форсингом

```python
# Рекомендуемый подход
check = engine.check(ctx, conditions)
if not check.ok:
    print(f"Условия нарушены: {check.violated}")
    return

result = engine.forces(ctx, phi, conditions)
```

### 2. Обрабатывайте все три случая TriBool

```python
# Рекомендуемый подход
result = engine.forces(ctx, phi, conds)

if result == TriBool.TRUE:
    do_something()
elif result == TriBool.FALSE:
    handle_false()
else:  # TriBool.UNKNOWN
    handle_unknown()

# Неполная обработка (не рекомендуется)
if result == TriBool.TRUE:
    do_something()
elif result == TriBool.FALSE:
    handle_false()
# Отсутствует обработка случая UNKNOWN
```

### 3. Используйте иммутабельные операции

```python
# Рекомендуемый подход - add возвращает новый объект
base_conds = Conditions()
extended_conds = base_conds.add(new_condition)

# Некорректный подход - add не изменяет исходный объект
conds = Conditions()
conds.add(condition)  # Результат игнорируется
```

### 4. Строите формулы композиционно

```python
# Рекомендуемый подход - переиспользуемые компоненты
is_valid_user = And((
    FactAtom("registered", (user,)),
    Not(FactAtom("banned", (user,)))
))

can_read = FactAtom("can_read", (user, doc))
can_write = FactAtom("can_write", (user, doc))

phi = And((is_valid_user, Or((can_read, can_write))))
```

### 5. Переиспользуйте движок

```python
# Рекомендуемый подход - создание один раз
engine = ForcingEngine(net)
for ctx in contexts:
    result = engine.forces(ctx, phi, conds)

# Неэффективный подход - множественные создания
for ctx in contexts:
    engine = ForcingEngine(net)
    result = engine.forces(ctx, phi, conds)
```

## Готовые сценарии

### Fast Smith (Быстрый Смит)

Классическая задача о динамике идентичности.

**Запуск:**
```bash
python src/ctmsn/examples/fast_smith_demo.py
```

**Что демонстрирует:**
- Композиции морфизмов (g ∘ h = j)
- Контекстную параметризацию
- Поведенческие предикаты (acts_like)
- Разность множеств (T⁻ = T \ T⁺)

**Подробности:** [scenarios/fast_smith/README.md](src/ctmsn/scenarios/fast_smith/README.md)

### Time Process (Процесс во времени)

Сценарий моделирования процессов во времени через композицию морфизмов.

**Запуск:**
```bash
python src/ctmsn/examples/time_process_demo.py
```

**Что демонстрирует:**
- Трёхуровневую формализацию (диаграмма → равенства → вычисление)
- Механизм вывода контекстных стрелок из before/after + sun
- Композиционные равенства с трассировкой (comp_expl)
- Режимы: sun (солнечный процесс) и prereq (prerequisite/effect)

**Пример вывода:**
```
=== TIME PROCESS: sun ===
Derivation stats: {'derived_edges_added': 4, 'comp_added': 8, 'comp_expl_added': 8}
forces(phi): true
Explain:
  - sunset = below ∘ sun_before (через узел T)
  - sunrise = above ∘ sun_after (через узел T)
```

**Подробности:** [scenarios/time_process/README.md](src/ctmsn/scenarios/time_process/README.md)

### Создание собственных сценариев

См. подробное руководство: [scenarios/README.md](src/ctmsn/scenarios/README.md)

## Дополнительная документация

- **[README.md](README.md)** — общий обзор проекта
- **[FORCING_IMPLEMENTATION.md](FORCING_IMPLEMENTATION.md)** — архитектура форсинг-движка
- **[FAST_SMITH_IMPLEMENTATION.md](FAST_SMITH_IMPLEMENTATION.md)** — реализация задачи о быстром Смите
- **[scenarios/README.md](src/ctmsn/scenarios/README.md)** — руководство по созданию сценариев
- **[scenarios/time_process/README.md](src/ctmsn/scenarios/time_process/README.md)** — процесс во времени
- **[.cursorrules](.cursorrules)** — правила кодирования проекта

## Текущие ограничения

### Реализовано

- Семантические сети (концепты, предикаты, факты)
- Параметризация (домены, переменные, контексты)
- Логические формулы (FactAtom, Not, And, Or, Implies, EqAtom)
- Трёхзначная логика (TRUE/FALSE/UNKNOWN)
- Проверка условий (`check`)
- Проверка форсирования (`forces`)
- Базовое расширение (`force` — skeleton)

### Не реализовано

- **Стратегии поиска** — `force()` не ищет расширения контекста
- **Кванторы** — нет ∀ (forall) и ∃ (exists)
- **Детальные объяснения** — explanation минимальны
- **Кэширование** — формулы пересчитываются каждый раз
- **Индексирование** — поиск фактов линейный O(n)
- **Constraint propagation** — нет сужения доменов
- **Визуализация** — нет графического отображения

### Планы развития 🚀

1. **Поисковые стратегии** (forcing/strategy.py)
   - Полный перебор (BruteEnumStrategy)
   - Поиск в глубину (DFS)
   - Поиск в ширину (BFS)
   - Эвристические стратегии

2. **Объяснения**
   - Трассировка вычислений
   - Граф зависимостей
   - Пояснения противоречий

3. **Кванторы**
   - Forall (∀x. φ)
   - Exists (∃x. φ)

4. **Оптимизации**
   - Кэширование результатов evaluate
   - Индексы для быстрого поиска фактов
   - Параллельная проверка условий

5. **Новые сценарии**
   - Планирование задач
   - Проверка безопасности
   - Конфигурационные правила
   - Эпистемическая логика

## Помощь и поддержка

При возникновении вопросов:

1. Прочитайте документацию в [FORCING_IMPLEMENTATION.md](FORCING_IMPLEMENTATION.md)
2. Изучите примеры в `src/ctmsn/examples/`
3. Посмотрите тесты в `tests/`
4. Создайте issue в репозитории (если применимо)

## Контрибуция

Вклад в проект приветствуется! См. CONTRIBUTING.md (если есть).

---

> **Навигация:** [🏠 Главная](README.md) | [← Назад](README.md#путь-новичка) | [Следующее: Архитектура форсинга →](FORCING_IMPLEMENTATION.md)

# Руководство по использованию CTMSN

## Быстрый старт

### 1. Активация виртуального окружения

```bash
source venv/bin/activate
```

### 2. Запуск примеров

```bash
# Простой пример
python src/ctmsn/examples/hello_forcing.py

# Расширенный пример со всеми кейсами
python src/ctmsn/examples/example_usage.py
```

### 3. Запуск тестов

```bash
python tests/test_smoke_imports.py
```

## Структура проекта

- `src/ctmsn/core/` - ядро семантической сети (концепты, предикаты, факты)
- `src/ctmsn/param/` - параметризация (домены, переменные, контексты)
- `src/ctmsn/logic/` - логический слой (формулы, оценка истинности)
- `src/ctmsn/forcing/` - форсинг-движок (расширение контекстов)
- `src/ctmsn/io/` - сериализация
- `src/ctmsn/examples/` - примеры использования

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

eng = ForcingEngine(net)

# Проверка: истинно ли phi в контексте?
result = eng.forces(ctx, phi, Conditions())
# result: TriBool.TRUE | TriBool.FALSE | TriBool.UNKNOWN

# Попытка расширить контекст чтобы phi стало истинным
force_result = eng.force(ctx, phi, Conditions())
print(force_result.status, force_result.explanation)
```

## Примеры сценариев

### Case 1: Формула уже истинна

```python
# Контекст полностью определён, phi истинно
# forces() вернёт TRUE
# force() вернёт TRUE с пояснением "Already forced"
```

### Case 2: Формула неопределена

```python
# Контекст неполный (не все переменные назначены)
# forces() вернёт UNKNOWN
# force() вернёт UNKNOWN с пояснением "Search not implemented yet"
```

### Case 3: Условия нарушены

```python
# Условия (constraints) не выполняются в контексте
# forces() вернёт FALSE
# force() вернёт FALSE с пояснением "Conditions or phi are false"
```

## Дальнейшее развитие

Текущая реализация - это каркас (skeleton). Для полноценной работы нужно:

1. Реализовать поисковые стратегии в `forcing/strategy.py`
2. Добавить механизм объяснений (explainability)
3. Расширить логический слой (кванторы, более сложные операторы)
4. Добавить полноценную сериализацию/десериализацию
5. Написать комплексные тесты
6. Создать практические задания для обучения

## Ограничения

- Только дискретные параметры
- Логика: AND/OR/NOT/IMPLIES
- Кванторы пока не реализованы
- Поиск расширений контекста (в `force()`) пока не реализован

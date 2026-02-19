# Реализация форсинг-движка CTMSN

> **Навигация:** [🏠 Главная](README.md) | [← Руководство пользователя](USAGE.md) | **Вы здесь: Архитектура форсинга** | [Следующее: Fast Smith →](FAST_SMITH_IMPLEMENTATION.md)

---

## 📖 Содержание

- [Обзор](#обзор)
- [Архитектура форсинга](#архитектура-форсинга)
- [Ключевые концепции](#ключевые-концепции)
- [Основные операции](#основные-операции)
- [Стратегии поиска](#стратегии-поиска)
- [Типичные сценарии](#типичные-сценарии-использования)
- [Оптимизации](#оптимизации-и-улучшения)
- [Тестирование](#тестирование-форсинга)
- [Лучшие практики](#лучшие-практики)

---

## Обзор

Форсинг-движок — это ключевой компонент библиотеки CTMSN, реализующий проверку и расширение контекстов для достижения логических целей в семантических сетях.

## Архитектура форсинга

### Основные компоненты

```
forcing/
├── engine.py       # Ядро форсинг-движка (ForcingEngine)
├── conditions.py   # Условия и ограничения (Conditions)
├── result.py       # Результаты работы (CheckResult, ForceResult)
└── strategy.py     # Стратегии поиска (Strategy, BruteEnumStrategy)

logic/
├── formula.py      # Логические формулы (Formula, FactAtom, And, Or, Not, ...)
├── evaluator.py    # Вычислитель истинности (evaluate)
├── tribool.py      # Трёхзначная логика (TriBool: TRUE/FALSE/UNKNOWN)
└── terms.py        # Термы (ConstTerm, VarTerm)
```

## Ключевые концепции

### 1. Трёхзначная логика (TriBool)

```python
from ctmsn.logic.tribool import TriBool

# Три возможных значения истинности
TriBool.TRUE      # Определённо истинно
TriBool.FALSE     # Определённо ложно
TriBool.UNKNOWN   # Неопределено (недостаточно информации)
```

**Семантика:**
- `TRUE` — формула истинна при полной интерпретации всех переменных
- `FALSE` — формула ложна даже при возможных расширениях контекста
- `UNKNOWN` — истинность зависит от неприсвоенных переменных

**Важно:** Не приводите `TriBool` к `bool` напрямую! Всегда используйте явные проверки:

```python
# ✅ Правильно
if result == TriBool.TRUE:
    ...

# ❌ Неправильно
if result:  # Будет True для любого значения кроме None!
    ...
```

### 2. Формулы (Formula)

Иерархия логических формул:

```python
# Базовый класс
class Formula:
    pass

# Атомарные формулы
@dataclass(frozen=True)
class FactAtom(Formula):
    predicate: str           # Имя предиката
    args: Tuple[Term, ...]   # Аргументы (концепты/переменные/строки)

@dataclass(frozen=True)
class EqAtom(Formula):
    left: Term               # Левый терм
    right: Term              # Правый терм

# Логические связки
@dataclass(frozen=True)
class Not(Formula):
    inner: Formula           # Отрицаемая формула

@dataclass(frozen=True)
class And(Formula):
    items: Tuple[Formula, ...]  # Конъюнкты

@dataclass(frozen=True)
class Or(Formula):
    items: Tuple[Formula, ...]  # Дизъюнкты

@dataclass(frozen=True)
class Implies(Formula):
    left: Formula            # Посылка
    right: Formula           # Следствие
```

**Примеры использования:**

```python
from ctmsn.logic.formula import FactAtom, Not, And, Or, Implies

# Простой факт: knows(alice, bob)
phi1 = FactAtom("knows", (alice, bob))

# Отрицание: ¬blocked(alice, bob)
phi2 = Not(FactAtom("blocked", (alice, bob)))

# Конъюнкция: knows(alice, bob) ∧ ¬blocked(alice, bob)
phi3 = And((phi1, phi2))

# Импликация: knows(x, y) → trusts(x, y)
phi4 = Implies(
    FactAtom("knows", (x, y)),
    FactAtom("trusts", (x, y))
)
```

### 3. Вычислитель (Evaluator)

Функция `evaluate()` вычисляет истинность формулы в контексте:

```python
from ctmsn.logic.evaluator import evaluate

def evaluate(
    formula: Formula,      # Формула для проверки
    net: SemanticNetwork, # Семантическая сеть
    ctx: Context          # Контекст (интерпретация переменных)
) -> TriBool:            # TRUE/FALSE/UNKNOWN
    ...
```

**Алгоритм:**

1. **FactAtom** — поиск совпадающего факта в сети
   - Разрешить все переменные в аргументах
   - Если есть неприсвоенная переменная → `UNKNOWN`
   - Найти факт с тем же предикатом и аргументами
   - Если найден → `TRUE`, иначе → `FALSE`

2. **EqAtom** — проверка равенства термов
   - Разрешить оба терма
   - Если хотя бы один неопределён → `UNKNOWN`
   - Сравнить значения → `TRUE`/`FALSE`

3. **Not** — отрицание
   - Вычислить внутреннюю формулу
   - `NOT(TRUE) = FALSE`
   - `NOT(FALSE) = TRUE`
   - `NOT(UNKNOWN) = UNKNOWN`

4. **And** — конъюнкция (короткое замыкание)
   - Если хотя бы один конъюнкт `FALSE` → `FALSE`
   - Если все `TRUE` → `TRUE`
   - Иначе → `UNKNOWN`

5. **Or** — дизъюнкция (короткое замыкание)
   - Если хотя бы один дизъюнкт `TRUE` → `TRUE`
   - Если все `FALSE` → `FALSE`
   - Иначе → `UNKNOWN`

6. **Implies** — импликация (A → B)
   - Если `A = FALSE` → `TRUE` (вакуумная истинность)
   - Если `A = TRUE` → вернуть значение `B`
   - Если `B = TRUE` → `TRUE` (независимо от A)
   - Иначе → `UNKNOWN`

### 4. Условия (Conditions)

Набор логических ограничений на контекст:

```python
from ctmsn.forcing.conditions import Conditions

# Создание пустого набора условий
conds = Conditions()

# Добавление условий (иммутабельно)
conds = conds.add(
    FactAtom("valid_user", (x,)),
    Not(FactAtom("blocked", (x,)))
)
```

**Семантика:**
- Условия должны быть истинны (`TRUE`) в контексте
- Если хотя бы одно условие `FALSE` — контекст невалиден
- Если есть `UNKNOWN` условия — контекст неполный, но может быть валидным

### 5. Форсинг-движок (ForcingEngine)

Главный класс для работы с форсингом:

```python
@dataclass
class ForcingEngine:
    net: SemanticNetwork

    def check(ctx, conditions) -> CheckResult
    def forces(ctx, phi, conditions) -> TriBool
    def force(ctx, phi, conditions, strategy) -> ForceResult
```

## Основные операции

### 1. check() — Проверка контекста

Проверяет, удовлетворяет ли контекст всем условиям:

```python
def check(
    self,
    ctx: Context,           # Проверяемый контекст
    conditions: Conditions  # Набор условий
) -> CheckResult:          # Результат проверки
    ...
```

**Алгоритм:**

```python
violated = []  # Нарушенные условия (FALSE)
unknown = []   # Неопределённые условия (UNKNOWN)

for i, condition in enumerate(conditions.items):
    v = evaluate(condition, net, ctx)
    if v is TriBool.FALSE:
        violated.append(f"cond[{i}]")
    elif v is TriBool.UNKNOWN:
        unknown.append(f"cond[{i}]")

return CheckResult(
    ok=(len(violated) == 0),  # OK, если нет нарушений
    violated=violated,
    unknown=unknown
)
```

**Результат:**

```python
@dataclass
class CheckResult:
    ok: bool              # True, если нет нарушенных условий
    violated: list[str]   # Список нарушенных условий
    unknown: list[str]    # Список неопределённых условий
```

**Интерпретация:**

| ok | violated | unknown | Значение |
|----|----------|---------|----------|
| ✅ | [] | [] | Контекст полностью валиден |
| ✅ | [] | ["cond[0]"] | Контекст неполный, но непротиворечив |
| ❌ | ["cond[1]"] | ... | Контекст противоречив (нарушено условие 1) |

**Пример:**

```python
engine = ForcingEngine(net)
conds = Conditions().add(
    FactAtom("adult", (person,)),
    Not(FactAtom("banned", (person,)))
)

result = engine.check(ctx, conds)
if not result.ok:
    print(f"Нарушены условия: {result.violated}")
```

### 2. forces() — Проверка форсирования

Проверяет, форсируется ли формула контекстом при заданных условиях:

```python
def forces(
    self,
    ctx: Context,           # Контекст
    phi: Formula,           # Целевая формула
    conditions: Conditions  # Условия
) -> TriBool:              # TRUE/FALSE/UNKNOWN
    ...
```

**Алгоритм:**

```python
# 1. Проверить условия
chk = self.check(ctx, conditions)
if not chk.ok:
    return TriBool.FALSE  # Условия нарушены → не форсирует

# 2. Вычислить формулу
v = evaluate(phi, net, ctx)

# 3. Определить результат
if v is TriBool.FALSE:
    return TriBool.FALSE  # Формула ложна → не форсирует

if v is TriBool.TRUE and len(chk.unknown) == 0:
    return TriBool.TRUE   # Формула истинна, условия определены → форсирует

return TriBool.UNKNOWN    # Недостаточно информации
```

**Семантика "форсирования":**

Контекст `ctx` **форсирует** формулу `φ` при условиях `C`, если:
1. Все условия из `C` истинны (или неопределены) в `ctx`
2. Формула `φ` истинна в `ctx`
3. Нет нарушенных условий

**Таблица истинности:**

| Условия | Формула φ | Результат |
|---------|-----------|-----------|
| ❌ FALSE | * | `FALSE` — условия нарушены |
| ✅ TRUE | ❌ FALSE | `FALSE` — формула ложна |
| ✅ TRUE | ✅ TRUE | `TRUE` — форсирует! |
| ⚠️ UNKNOWN | ✅ TRUE | `UNKNOWN` — неполная информация |
| ✅ TRUE | ⚠️ UNKNOWN | `UNKNOWN` — неполная информация |

**Пример:**

```python
engine = ForcingEngine(net)

phi = And((
    FactAtom("can_access", (user, resource)),
    FactAtom("has_permission", (user, perm))
))

result = engine.forces(ctx, phi, conditions)

if result == TriBool.TRUE:
    print("Доступ разрешён")
elif result == TriBool.FALSE:
    print("Доступ запрещён")
else:
    print("Недостаточно информации для решения")
```

### 3. force() — Расширение контекста

Пытается расширить контекст так, чтобы формула стала истинной:

```python
def force(
    self,
    ctx: Context,                    # Исходный контекст
    phi: Formula,                    # Целевая формула
    conditions: Conditions,          # Условия
    strategy: Strategy | None = None # Стратегия поиска
) -> ForceResult:                   # Результат форсирования
    ...
```

**Алгоритм (текущая реализация — skeleton):**

```python
strategy = strategy or BruteEnumStrategy()

# 1. Проверить текущий статус
cur = self.forces(ctx, phi, conditions)

# 2. Если уже форсирует — вернуть как есть
if cur is TriBool.TRUE:
    return ForceResult(
        status=TriBool.TRUE,
        context=ctx,
        explanation="Already forced"
    )

# 3. Если противоречие — невозможно форсировать
if cur is TriBool.FALSE:
    return ForceResult(
        status=TriBool.FALSE,
        context=None,
        explanation="Conditions or phi are false"
    )

# 4. Если неопределено — нужен поиск (пока не реализован)
return ForceResult(
    status=TriBool.UNKNOWN,
    context=None,
    explanation="Search not implemented yet"
)
```

**Результат:**

```python
@dataclass
class ForceResult:
    status: TriBool        # TRUE/FALSE/UNKNOWN
    context: Any | None    # Расширенный контекст (если найден)
    explanation: str | None # Пояснение результата
```

**Возможные результаты:**

| status | context | explanation | Значение |
|--------|---------|-------------|----------|
| `TRUE` | ctx | "Already forced" | Формула уже истинна |
| `FALSE` | None | "Conditions or phi are false" | Невозможно форсировать |
| `UNKNOWN` | None | "Search not implemented yet" | Поиск не реализован |
| `TRUE` | new_ctx | "Found extension" | Найдено расширение (будущее) |
| `FALSE` | None | "No valid extension exists" | Расширений не существует (будущее) |

**Пример:**

```python
engine = ForcingEngine(net)

# Попытаться форсировать доступ
result = engine.force(ctx, phi, conditions)

if result.status == TriBool.TRUE:
    print(f"Успех: {result.explanation}")
    if result.context != ctx:
        print(f"Контекст расширен: {result.context.as_dict()}")
elif result.status == TriBool.FALSE:
    print(f"Невозможно: {result.explanation}")
else:
    print(f"Неопределено: {result.explanation}")
```

## Стратегии поиска

### Текущая реализация (Skeleton)

```python
class Strategy:
    def candidates(
        self,
        ctx: Context,
        vars_to_assign: list[Variable]
    ) -> Iterable[Mapping[Variable, Any]]:
        raise NotImplementedError


@dataclass
class BruteEnumStrategy(Strategy):
    max_branch: int = 2000

    def candidates(self, ctx, vars_to_assign):
        yield {}  # Пока ничего не генерирует
```

**Статус:** Заглушка. Возвращает пустое расширение.

### Будущие стратегии

#### 1. Полный перебор (Brute Force)

```python
class BruteEnumStrategy(Strategy):
    def candidates(self, ctx, vars_to_assign):
        # Генерировать все комбинации значений
        for assignment in product(*[var.domain.values for var in vars_to_assign]):
            yield dict(zip(vars_to_assign, assignment))
```

**Сложность:** O(|D₁| × |D₂| × ... × |Dₙ|), где Dᵢ — домен i-й переменной

**Подходит для:**
- Маленьких доменов (< 10 значений)
- Небольшого числа переменных (< 5)

#### 2. Поиск в глубину (DFS)

```python
class DFSStrategy(Strategy):
    def candidates(self, ctx, vars_to_assign):
        # Рекурсивно назначать переменные
        # Откатываться при нарушении условий
        ...
```

**Преимущества:**
- Память O(n), где n — число переменных
- Ранний откат при нарушениях

#### 3. Поиск в ширину (BFS)

```python
class BFSStrategy(Strategy):
    def candidates(self, ctx, vars_to_assign):
        # Послойно расширять контекст
        # Гарантия минимального расширения
        ...
```

**Преимущества:**
- Находит минимальное расширение
- Полнота поиска

#### 4. Эвристические стратегии

```python
class HeuristicStrategy(Strategy):
    def candidates(self, ctx, vars_to_assign):
        # Сортировать переменные по эвристике
        # (например, минимальный домен первым)
        # Использовать propagation для ограничения доменов
        ...
```

**Эвристики:**
- **Minimum Remaining Values (MRV)** — сначала переменные с наименьшим доменом
- **Degree heuristic** — сначала переменные с большим числом ограничений
- **Least Constraining Value** — сначала значения, оставляющие больше свободы

## Типичные сценарии использования

### Сценарий 1: Проверка валидности

```python
# Проверить, что пользователь имеет право доступа
engine = ForcingEngine(net)

conditions = Conditions().add(
    FactAtom("registered", (user,)),
    Not(FactAtom("banned", (user,)))
)

ctx = Context()
ctx.set(user_var, alice)

# Проверка условий
check = engine.check(ctx, conditions)
if not check.ok:
    print(f"Пользователь не валиден: {check.violated}")

# Проверка конкретного права
phi = FactAtom("can_edit", (user, document))
if engine.forces(ctx, phi, conditions) == TriBool.TRUE:
    print("Редактирование разрешено")
```

### Сценарий 2: Поиск допустимого назначения

```python
# Найти подходящего исполнителя для задачи
engine = ForcingEngine(net)

conditions = Conditions().add(
    FactAtom("has_skill", (worker, required_skill)),
    Not(FactAtom("overloaded", (worker,)))
)

phi = FactAtom("can_perform", (worker, task))

# Пока что вернёт UNKNOWN (поиск не реализован)
result = engine.force(empty_ctx, phi, conditions)

# В будущем: найдёт worker, удовлетворяющего условиям
if result.status == TriBool.TRUE:
    assigned_worker = result.context.get(worker_var)
    print(f"Назначен: {assigned_worker}")
```

### Сценарий 3: Валидация конфигурации

```python
# Проверить, что конфигурация непротиворечива
engine = ForcingEngine(net)

# Ограничения конфигурации
conditions = Conditions().add(
    # Если выбран режим A, то параметр X должен быть установлен
    Implies(
        FactAtom("mode", (config, mode_a)),
        FactAtom("has_param", (config, param_x))
    ),
    # Режимы A и B взаимно исключающи
    Not(And((
        FactAtom("mode", (config, mode_a)),
        FactAtom("mode", (config, mode_b))
    )))
)

check = engine.check(current_config, conditions)
if not check.ok:
    print(f"Конфигурация невалидна: {check.violated}")
elif check.unknown:
    print(f"Конфигурация неполная: {check.unknown}")
else:
    print("Конфигурация валидна")
```

### Сценарий 4: Композиция поведений (Fast Smith)

```python
# Проверка композиционных равенств
engine = ForcingEngine(net)

A = net.concepts["A"]

# Условия: композиции морфизмов
conditions = Conditions().add(
    FactAtom("comp", ("h", "g", "j")),        # g ∘ h = j
    FactAtom("comp", ("h", "not-g", "s")),    # not-g ∘ h = s
    FactAtom("comp", ("sf", "r", "jf"))       # r ∘ sf = jf
)

# Цель: A ведёт себя как j, s и jf одновременно
phi = And((
    FactAtom("acts_like", (A, "j")),
    FactAtom("acts_like", (A, "s")),
    FactAtom("acts_like", (A, "jf"))
))

ctx = Context()
ctx.set(node_var, A)

result = engine.forces(ctx, phi, conditions)
# → TRUE (все факты присутствуют в сети)
```

## Оптимизации и улучшения

### Текущие ограничения

1. **Поиск не реализован** — `force()` не умеет расширять контекст
2. **Нет кэширования** — формулы пересчитываются каждый раз
3. **Нет индексов** — поиск фактов линейный
4. **Нет объяснений** — explanation минимальны
5. **Нет кванторов** — только пропозициональная логика с переменными

### Возможные улучшения

#### 1. Кэширование результатов

```python
@dataclass
class ForcingEngine:
    net: SemanticNetwork
    _eval_cache: dict[tuple[Formula, frozenset], TriBool] = field(default_factory=dict)

    def forces(self, ctx, phi, conditions):
        cache_key = (phi, frozenset(ctx.as_dict().items()))
        if cache_key in self._eval_cache:
            return self._eval_cache[cache_key]
        
        result = self._forces_impl(ctx, phi, conditions)
        self._eval_cache[cache_key] = result
        return result
```

#### 2. Индексирование фактов

```python
# В SemanticNetwork добавить индексы
_facts_by_predicate_and_first_arg: dict[tuple[str, Any], set[Statement]]

# Ускорить поиск при известном первом аргументе
facts = net._facts_by_predicate_and_first_arg.get((predicate, first_arg), set())
```

#### 3. Трассировка вычислений

```python
@dataclass
class EvaluationTrace:
    formula: Formula
    result: TriBool
    sub_traces: list[EvaluationTrace]
    explanation: str

def evaluate_with_trace(formula, net, ctx) -> tuple[TriBool, EvaluationTrace]:
    # Рекурсивно собирать трассу вычисления
    ...
```

#### 4. Constraint propagation

```python
def propagate_constraints(ctx, conditions, vars_to_assign):
    # Для каждой неприсвоенной переменной
    # Сузить её домен, исключив значения,
    # приводящие к нарушению условий
    ...
```

#### 5. Кванторы

```python
@dataclass(frozen=True)
class Forall(Formula):
    var: Variable
    body: Formula

@dataclass(frozen=True)
class Exists(Formula):
    var: Variable
    body: Formula

# В evaluator:
def evaluate(formula, net, ctx):
    if isinstance(formula, Forall):
        # Проверить для всех значений в домене
        ...
    if isinstance(formula, Exists):
        # Проверить существование хотя бы одного значения
        ...
```

## Тестирование форсинга

### Базовые тесты

```python
def test_forces_true_when_fact_exists():
    net = SemanticNetwork()
    alice = Concept("alice", "Alice")
    net.add_concept(alice)
    net.add_predicate(Predicate("adult", 1))
    net.assert_fact("adult", (alice,))
    
    ctx = Context()
    phi = FactAtom("adult", (alice,))
    
    engine = ForcingEngine(net)
    assert engine.forces(ctx, phi, Conditions()) == TriBool.TRUE


def test_forces_false_when_fact_missing():
    net = SemanticNetwork()
    alice = Concept("alice", "Alice")
    net.add_concept(alice)
    net.add_predicate(Predicate("admin", 1))
    
    ctx = Context()
    phi = FactAtom("admin", (alice,))
    
    engine = ForcingEngine(net)
    assert engine.forces(ctx, phi, Conditions()) == TriBool.FALSE


def test_forces_unknown_when_variable_unassigned():
    net = SemanticNetwork()
    net.add_predicate(Predicate("adult", 1))
    
    x = Variable("x", EnumDomain((alice, bob)))
    ctx = Context()  # x не присвоена
    phi = FactAtom("adult", (x,))
    
    engine = ForcingEngine(net)
    assert engine.forces(ctx, phi, Conditions()) == TriBool.UNKNOWN
```

### Тесты условий

```python
def test_check_ok_when_all_conditions_true():
    net = SemanticNetwork()
    alice = Concept("alice", "Alice")
    net.add_concept(alice)
    net.add_predicate(Predicate("valid", 1))
    net.assert_fact("valid", (alice,))
    
    ctx = Context()
    conds = Conditions().add(FactAtom("valid", (alice,)))
    
    engine = ForcingEngine(net)
    result = engine.check(ctx, conds)
    
    assert result.ok
    assert len(result.violated) == 0
    assert len(result.unknown) == 0


def test_check_not_ok_when_condition_violated():
    net = SemanticNetwork()
    alice = Concept("alice", "Alice")
    net.add_concept(alice)
    net.add_predicate(Predicate("banned", 1))
    net.assert_fact("banned", (alice,))
    
    ctx = Context()
    conds = Conditions().add(Not(FactAtom("banned", (alice,))))
    
    engine = ForcingEngine(net)
    result = engine.check(ctx, conds)
    
    assert not result.ok
    assert len(result.violated) == 1
```

### Тесты сложных формул

```python
def test_and_formula():
    net = SemanticNetwork()
    alice = Concept("alice", "Alice")
    net.add_concept(alice)
    net.add_predicate(Predicate("adult", 1))
    net.add_predicate(Predicate("verified", 1))
    net.assert_fact("adult", (alice,))
    net.assert_fact("verified", (alice,))
    
    ctx = Context()
    phi = And((
        FactAtom("adult", (alice,)),
        FactAtom("verified", (alice,))
    ))
    
    engine = ForcingEngine(net)
    assert engine.forces(ctx, phi, Conditions()) == TriBool.TRUE


def test_implies_formula():
    net = SemanticNetwork()
    alice = Concept("alice", "Alice")
    net.add_concept(alice)
    net.add_predicate(Predicate("premium", 1))
    net.add_predicate(Predicate("can_download", 1))
    net.assert_fact("premium", (alice,))
    net.assert_fact("can_download", (alice,))
    
    ctx = Context()
    phi = Implies(
        FactAtom("premium", (alice,)),
        FactAtom("can_download", (alice,))
    )
    
    engine = ForcingEngine(net)
    assert engine.forces(ctx, phi, Conditions()) == TriBool.TRUE
```

## Лучшие практики

### 1. Проверяйте условия перед форсингом

```python
# ✅ Правильно
check = engine.check(ctx, conditions)
if check.ok:
    result = engine.forces(ctx, phi, conditions)
else:
    print(f"Условия нарушены: {check.violated}")

# ❌ Неправильно (лишняя работа)
result = engine.forces(ctx, phi, conditions)
if result == TriBool.FALSE:
    # Почему? Условия? Формула? Непонятно.
    ...
```

### 2. Используйте иммутабельные условия

```python
# ✅ Правильно
base_conds = Conditions().add(common_constraint)
specific_conds = base_conds.add(specific_constraint)

# ❌ Неправильно (условия иммутабельны!)
conds = Conditions()
conds.add(constraint)  # Вернёт новый объект, исходный не изменится!
```

### 3. Обрабатывайте все три случая

```python
# ✅ Правильно
result = engine.forces(ctx, phi, conds)
if result == TriBool.TRUE:
    # Форсирует
elif result == TriBool.FALSE:
    # Не форсирует (противоречие)
else:  # TriBool.UNKNOWN
    # Недостаточно информации

# ❌ Неправильно (забыли UNKNOWN)
if result == TriBool.TRUE:
    ...
elif result == TriBool.FALSE:
    ...
# Что если UNKNOWN? Упадёт дальше в коде!
```

### 4. Переиспользуйте движок

```python
# ✅ Правильно
engine = ForcingEngine(net)
for ctx in contexts:
    result = engine.forces(ctx, phi, conds)

# ❌ Неправильно (лишние объекты)
for ctx in contexts:
    engine = ForcingEngine(net)  # Новый каждый раз
    result = engine.forces(ctx, phi, conds)
```

### 5. Строите формулы композиционно

```python
# ✅ Правильно
can_access = FactAtom("can_access", (user, resource))
has_permission = FactAtom("has_permission", (user, perm))
not_banned = Not(FactAtom("banned", (user,)))

phi = And((can_access, has_permission, not_banned))

# ❌ Неправильно (сложно читать и модифицировать)
phi = And((
    FactAtom("can_access", (user, resource)),
    FactAtom("has_permission", (user, perm)),
    Not(FactAtom("banned", (user,)))
))
```

## Заключение

Форсинг-движок CTMSN реализует базовую проверку истинности формул в контекстах с условиями, используя трёхзначную логику.

**Текущие возможности:**
- Проверка условий (`check`)
- Проверка форсирования (`forces`)
- Базовое расширение контекста (`force` — skeleton)
- Трёхзначная логика (TRUE/FALSE/UNKNOWN)
- Набор формул (FactAtom, Not, And, Or, Implies, EqAtom)
- Композиция условий

**Направления развития:**
- Стратегии поиска (BFS, DFS, эвристики)
- Кэширование и индексирование
- Детальные объяснения (explanation)
- Кванторы (∀, ∃)
- Constraint propagation
- Параллельный поиск

**Готово к использованию для:**
- Проверки валидности контекстов
- Верификации логических утверждений
- Демонстрации концепций форсинга
- Обучения семантическим сетям

---

**Дата документации:** 19 февраля 2026  
**Версия библиотеки:** CTMSN 0.1.0  
**Python:** 3.9+

---

> **Навигация:** [🏠 Главная](README.md) | [← Руководство пользователя](USAGE.md) | [Следующее: Fast Smith →](FAST_SMITH_IMPLEMENTATION.md)
> 
> **См. также:**
> - [Руководство по созданию сценариев](src/ctmsn/scenarios/README.md)
> - [Полный обзор документации](DOCUMENTATION_SUMMARY.md)

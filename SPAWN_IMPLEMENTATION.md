# Spawn (4.15) — Реализация

> **Навигация:** [🏠 Главная](README.md) | [← Fishing](FISHING_IMPLEMENTATION.md) | **Вы здесь: Spawn** | [Руководство пользователя →](USAGE.md)

## 📖 Содержание

- [Описание задачи](#описание-задачи)
- [Математическая модель](#математическая-модель)
- [Архитектура реализации](#архитектура-реализации)
- [Алгоритм вывода композиций](#алгоритм-вывода-композиций)
- [Канонические равенства](#канонические-равенства)
- [Примеры использования](#примеры-использования)

> **См. также:**
> - [USAGE.md](USAGE.md) — примеры использования
> - [FORCING_IMPLEMENTATION.md](FORCING_IMPLEMENTATION.md) — детали форсинг-движка
> - [scenarios/spawn/README.md](src/ctmsn/scenarios/spawn/README.md) — описание сценария

## Описание задачи

Задача о нересте рыб (4.15) моделирует процесс изменения ролей (самка/самец) и поведения (поедание икры) у рыб через стадии развития A → B → C. Ключевая особенность — доказательство композиций с поведенческими операторами `push` и `rethink` на разных стадиях времени.

### Сущности модели

**Стадии процесса:**
- `A` — начальная стадия
- `B` — промежуточная стадия (позже A)
- `C` — финальная стадия (позже B)

**Состояния рыб:**
- `Fish` — базовое состояние "рыба"
- `Fish_minus` (Fish⁻) — рыбы, не едящие икру
- `Fish_plus` (Fish⁺) — рыбы, едящие икру

**Роли:**
- `spawner` — самка (не ест икру)
- `milter` — самец (ест икру)

**Контексты:**
- `Cf_minus` (C_f⁻) — контекст "не едят икру" под развитием f
- `Cf_plus` (C_f⁺) — контекст "едят икру" под развитием f
- `Cf_plus_fe` (C_f⁺)_e — контекст "едят икру" под развитием f∘e

## Математическая модель

### Диаграмма отношений

```
       f            e
    B ───→ A     C ───→ B

    fish: A → Fish
    not_eat: Fish → Fish_minus  (spawner)
    eat: Fish → Fish_plus       (milter)

    push: Fish_plus → Fish_minus      (отталкивание)
    rethink: Fish_minus → Fish_plus   (передумать)
```

### Базовые определения

**Роли как композиции:**
```
spawner = not-eat ∘ fish  (A → Fish_minus)
milter = eat ∘ fish       (A → Fish_plus)
```

**Протяжка по времени (f и e):**
```
spawner_f = spawner после развития f  (B → Fish_minus)
milter_f = milter после развития f    (B → Fish_plus)

spawner_fe = spawner_f после развития e  (C → Fish_minus)
milter_fe = milter_f после развития e    (C → Fish_plus)
```

### Канонические равенства

**На стадии A:**
```
spawner = not-eat ∘ fish
milter = eat ∘ fish
```

**На стадии B (после развития f):**
```
push ∘ milter_f = spawner_f
rethink ∘ spawner_f = milter_f
rethink ∘ push ∘ milter_f = milter_f
```

**На стадии C (после развития f∘e):**
```
(rethink ∘ spawner_f)_e = (milter_f)_e
```

## Архитектура реализации

### Структура модулей

```
scenarios/spawn/
├── model.py          # Граф: узлы, стрелки
├── derive.py         # Вывод композиций
├── constraints.py    # Условия (равенства)
├── goal.py           # Целевая формула
├── explain.py        # Объяснения
└── runner.py         # Главный запуск
```

### Модель данных (`model.py`)

#### Концепты (вершины графа)

**Стадии процесса:**
```python
A = Concept("A", "Stage A")
B = Concept("B", "Stage B (later than A)")
C = Concept("C", "Stage C (later than B)")
```

**Состояния рыб:**
```python
Fish = Concept("Fish", "Fish")
Fish_m = Concept("Fish_minus", "Fish- (not eat eggs)")
Fish_p = Concept("Fish_plus", "Fish+ (eat eggs)")
```

**Контексты:**
```python
Cf_m = Concept("Cf_minus", "C_f- (not eat eggs under f)")
Cf_p = Concept("Cf_plus", "C_f+ (eat eggs under f)")
Cf_p_fe = Concept("Cf_plus_fe", "(C_f+)_fe (eat eggs under f∘e)")
```

#### Предикаты

```python
edge(label, from, to)           # Базовые стрелки
derived_edge(label, from, to)   # Выведенные стрелки
comp2(left, right, result)      # 2-шаговые композиции
comp2_expl(left, right, result, mid)  # С объяснением
compN(chain, result)            # N-шаговые композиции
compN_expl(chain, result, trace)      # С трассировкой
```

#### Базовые стрелки

**Эволвенты (развитие по времени):**
```python
net.assert_fact("edge", ("f", B, A))
net.assert_fact("edge", ("e", C, B))
```

**Базовое отображение на стадии A:**
```python
net.assert_fact("edge", ("fish", A, Fish))
net.assert_fact("edge", ("not_eat", Fish, Fish_m))
net.assert_fact("edge", ("eat", Fish, Fish_p))
```

**Именованные результаты:**
```python
net.assert_fact("edge", ("spawner", A, Fish_m))
net.assert_fact("edge", ("milter", A, Fish_p))
```

**Поведенческие операторы:**
```python
net.assert_fact("edge", ("push", Fish_p, Fish_m))
net.assert_fact("edge", ("rethink", Fish_m, Fish_p))
```

**Результаты на стадиях B и C:**
```python
net.assert_fact("edge", ("spawner_f", B, Fish_m))
net.assert_fact("edge", ("milter_f", B, Fish_p))
net.assert_fact("edge", ("spawner_fe", C, Fish_m))
net.assert_fact("edge", ("milter_fe", C, Fish_p))
```

## Алгоритм вывода композиций

### D1: Протяжка стрелок по времени

Функция `derive_context_edges(net)` выводит стрелки с временными индексами.

#### Алгоритм

```
Для каждой пары (эволвент, стрелка):
  Если есть f: B → A и label: A → Z
    Создать derived_edge("label_f", B, Z)
  
  Если есть e: C → B и label_f: B → Z
    Создать derived_edge("label_fe", C, Z)
```

#### Примеры выводов

```
f: B → A, spawner: A → Fish_minus
  ⇒ spawner_f: B → Fish_minus

e: C → B, spawner_f: B → Fish_minus
  ⇒ spawner_fe: C → Fish_minus
```

### D2.1: Двухшаговые композиции (comp2)

Функция `derive_comp2(net)` находит все 2-шаговые пути с именованными результатами.

#### Алгоритм

```
Для каждой пары стрелок (left, right):
  left: X → Y
  right: Y → Z
  
  Для каждого именованного result: X → Z:
    Если result существует как стрелка:
      Создать comp2(left, right, result)
      Создать comp2_expl(left, right, result, mid=Y)
```

#### Примеры выводов

```
fish: A → Fish, not_eat: Fish → Fish_minus
spawner: A → Fish_minus (существует)
  ⇒ comp2("fish", "not_eat", "spawner")
  ⇒ comp2_expl("fish", "not_eat", "spawner", mid="Fish")

milter_f: B → Fish_plus, push: Fish_plus → Fish_minus
spawner_f: B → Fish_minus (существует)
  ⇒ comp2("milter_f", "push", "spawner_f")
  ⇒ comp2_expl("milter_f", "push", "spawner_f", mid="Fish_plus")
```

### D2.2: Многошаговые композиции (compN)

Функция `derive_compN(net, start, chain, result_label, chain_name)` проверяет N-шаговые пути.

#### Алгоритм

```
Вход:
  start — начальная вершина
  chain — список меток [label1, label2, ..., labelN]
  result_label — ожидаемая итоговая стрелка
  chain_name — имя цепочки для записи

Шаг 1: Построить путь по цепочке
  cur = {start}
  trace = []
  Для каждой метки в chain:
    Найти все достижимые вершины через метку
    cur = {все достижимые из cur через метку}
    Добавить в trace

Шаг 2: Проверить именованный результат
  Для каждой конечной вершины end в cur:
    Если существует стрелка result_label: start → end:
      Создать compN(chain_name, result_label)
      Создать compN_expl(chain_name, result_label, trace)
      Вернуть True
  
  Вернуть False
```

#### Пример 1: Трёхшаговая композиция на стадии B

```
Вход:
  start = "B"
  chain = ["milter_f", "push", "rethink"]
  result_label = "milter_f"
  chain_name = "rethink∘push∘milter_f"

Выполнение:
  B --milter_f--> Fish_plus --push--> Fish_minus --rethink--> Fish_plus
  
Проверка:
  Есть milter_f: B → Fish_plus? Да.
  
Результат:
  compN("rethink∘push∘milter_f", "milter_f")
  compN_expl("rethink∘push∘milter_f", "milter_f", "start=B; milter_f->['Fish_plus']; push->['Fish_minus']; rethink->['Fish_plus']; end=Fish_plus")
```

#### Пример 2: Композиция на стадии C

```
Вход:
  start = "C"
  chain = ["e", "spawner_f", "rethink"]
  result_label = "milter_fe"
  chain_name = "(rethink∘spawner_f)_e"

Выполнение:
  C --e--> B --spawner_f--> Fish_minus --rethink--> Fish_plus
  
Проверка:
  Есть milter_fe: C → Fish_plus? Да.
  
Результат:
  compN("(rethink∘spawner_f)_e", "milter_fe")
  compN_expl("(rethink∘spawner_f)_e", "milter_fe", "start=C; e->['B']; spawner_f->['Fish_minus']; rethink->['Fish_plus']; end=Fish_plus")
```

## Канонические равенства

### Полный список равенств

```python
# Стадия A: Определение ролей
comp2("fish", "not_eat", "spawner")
comp2("fish", "eat", "milter")

# Стадия B: Поведенческие операторы
comp2("milter_f", "push", "spawner_f")
comp2("spawner_f", "rethink", "milter_f")

# Стадия B: Длинная композиция
compN("rethink∘push∘milter_f", "milter_f")

# Стадия C: Протяжка композиции
compN("(rethink∘spawner_f)_e", "milter_fe")
```

### Семантика равенств

**Равенство 1:** `spawner = not-eat ∘ fish`
- Самка определяется как рыба, которая не ест икру

**Равенство 2:** `milter = eat ∘ fish`
- Самец определяется как рыба, которая ест икру

**Равенство 3:** `push ∘ milter_f = spawner_f`
- Отталкивание самца превращает его в самку (на стадии B)

**Равенство 4:** `rethink ∘ spawner_f = milter_f`
- Самка может передумать и стать самцом (на стадии B)

**Равенство 5:** `rethink ∘ push ∘ milter_f = milter_f`
- Отталкивание и передумывание возвращает самца в исходное состояние

**Равенство 6:** `(rethink ∘ spawner_f)_e = (milter_f)_e`
- На стадии C композиция передумывания сохраняется

## Примеры использования

### Базовый запуск

```python
from ctmsn.scenarios.spawn.runner import run

result = run()
print("Derivation:", result["derivation"])
print("Check:", result["check"].ok)
print("Forces:", result["forces"].value)
```

### Объяснения выводов

```python
from ctmsn.scenarios.spawn.explain import explain_comp2, explain_compN
from ctmsn.scenarios.spawn.model import build_network
from ctmsn.scenarios.spawn.derive import apply as derive_apply

net = build_network()
derive_apply(net)

# Объяснение 2-шаговой композиции
lines = explain_comp2(net, "fish", "not_eat", "spawner")
for line in lines:
    print(line)

# Объяснение многошаговой композиции
lines = explain_compN(net, "rethink∘push∘milter_f", "milter_f")
for line in lines:
    print(line)
```

### Вывод

```
spawner = not_eat ∘ fish (через Fish)
milter_f = rethink∘push∘milter_f (trace: start=B; milter_f->['Fish_plus']; push->['Fish_minus']; rethink->['Fish_plus']; end=Fish_plus)
```

### Полный цикл с форсингом

```python
from ctmsn.param.context import Context
from ctmsn.forcing.engine import ForcingEngine
from ctmsn.scenarios.spawn.model import build_network
from ctmsn.scenarios.spawn.derive import apply as derive_apply
from ctmsn.scenarios.spawn.constraints import build_conditions
from ctmsn.scenarios.spawn.goal import build_goal

# Построение модели
net = build_network()
derive_apply(net)

# Форсинг
eng = ForcingEngine(net)
ctx = Context()
conds = build_conditions()
phi = build_goal()

# Проверка условий
chk = eng.check(ctx, conds)
print("Conditions OK:", chk.ok)

# Проверка форсирования
forces = eng.forces(ctx, phi, conds)
print("Forces φ:", forces.value)

# Попытка форсировать
result = eng.force(ctx, phi, conds)
print("Force status:", result.status.value)
print("Explanation:", result.explanation)
```

### Ожидаемый вывод

```
Conditions OK: True
Forces φ: true
Force status: true
Explanation: Already forced
```

## Граничные случаи

### Отсутствие стрелок

Если в графе нет базовых стрелок `fish`, `not_eat`, `eat`, выводы не создаются:
```python
# Пустой граф — нет выводов
assert derive_context_edges(empty_net) == 0
assert derive_comp2(empty_net) == 0
```

### Неполная цепочка

Если в цепочке отсутствует промежуточная стрелка, compN возвращает False:
```python
# Нет стрелки "push" — цепочка не строится
ok = derive_compN(net, "B", ["milter_f", "missing", "rethink"], "milter_f", "broken_chain")
assert ok is False
```

### Несовпадение результата

Если путь существует, но нет именованного результата, compN не создаётся:
```python
# Путь B → Fish_plus → Fish_minus → Fish_plus есть,
# но нет стрелки "wrong_result": B → Fish_plus
ok = derive_compN(net, "B", ["milter_f", "push", "rethink"], "wrong_result", "test")
assert ok is False
```

## Тестирование

### Тесты построения

```python
def test_network_builds():
    net = build_network()
    assert "A" in net.concepts
    assert "Fish" in net.concepts
```

### Тесты вывода

```python
def test_derive_comp2():
    net = build_network()
    derive_context_edges(net)
    added = derive_comp2(net)
    assert added > 0
```

### Тесты целей

```python
def test_forces_goal():
    net = build_network()
    derive_apply(net)
    
    conds = build_conditions()
    phi = build_goal()
    
    eng = ForcingEngine(net)
    ctx = Context()
    
    result = eng.forces(ctx, phi, conds)
    assert result == TriBool.TRUE
```

---

> **Навигация:** [🏠 Главная](README.md) | [← Fishing](FISHING_IMPLEMENTATION.md) | **Вы здесь: Spawn** | [Руководство пользователя →](USAGE.md)

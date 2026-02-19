# CTMSN - Composable Typed Modules for Semantic Networks

> **Навигация:** **Вы здесь: Главная** | [Руководство пользователя →](USAGE.md) | [Карта документации →](NAVIGATION.md)

CTMSN — библиотека на Python для работы с семантическими сетями, параметризацией и форсингом.  
Ядро библиотеки (`src/ctmsn`) использует только стандартную библиотеку Python.

## 📖 Содержание
- [Что в проекте](#что-в-проекте)
- [Быстрый старт (ядро)](#быстрый-старт-ядро)
- [Локальный UI (API + Web)](#локальный-ui-api--web)
- [Структура проекта](#структура-проекта)
- [Сценарии и примеры](#сценарии-и-примеры)
- [Тестирование](#тестирование)
- [Документация](#документация)
- [Текущее состояние](#текущее-состояние)

## Что в проекте
- Семантическая сеть: `Concept`, `Predicate`, `Statement`, `SemanticNetwork`
- Параметризация: `Domain`, `Variable`, `Context`
- Логика: `FactAtom`, `EqAtom`, `Not`, `And`, `Or`, `Implies`, `TriBool`
- Форсинг: `ForcingEngine.check()`, `ForcingEngine.forces()`, `ForcingEngine.force()`
- Сценарии: `fast_smith`, `time_process`, `fishing`, `spawn`
- Веб-приложение: `apps/api` (FastAPI), `apps/web` (Next.js)

## Быстрый старт (ядро)

```bash
pip3 install -e .
python3 src/ctmsn/examples/hello_forcing.py
python3 src/ctmsn/examples/fast_smith_demo.py
```

Дополнительные примеры:

```bash
python3 src/ctmsn/examples/time_process_demo.py
python3 src/ctmsn/examples/fishing_demo.py
python3 src/ctmsn/examples/spawn_demo.py
python3 src/ctmsn/examples/example_usage.py
```

## Локальный UI (API + Web)

```bash
source venv/bin/activate
make install
make dev
```

Сервисы после запуска:
- Web: `http://localhost:3000`
- API: `http://127.0.0.1:8000`

См. также:
- [apps/api/README.md](apps/api/README.md)
- [apps/web/README.md](apps/web/README.md)
- [UI_IMPLEMENTATION.md](UI_IMPLEMENTATION.md)

## Структура проекта

```text
src/ctmsn/
├── core/        # Примитивы семантической сети
├── param/       # Домены, переменные, контексты
├── logic/       # Формулы, термы, TriBool, evaluator
├── forcing/     # ForcingEngine, conditions, result, strategy
├── scenarios/   # fast_smith, time_process, fishing, spawn
├── examples/    # hello_forcing и демо-сценарии
└── io/          # сериализация

apps/
├── api/         # FastAPI backend (auth, workspaces, editors, teacher)
└── web/         # Next.js frontend

tests/
├── test_*.py            # базовые проверки ядра
├── scenarios/test_*.py  # проверки сценариев
└── e2e_*.py             # end-to-end тесты UI
```

## Сценарии и примеры

Реализованные сценарии:
- [Fast Smith](src/ctmsn/scenarios/fast_smith/README.md)
- [Time Process](src/ctmsn/scenarios/time_process/README.md)
- [Fishing](src/ctmsn/scenarios/fishing/README.md)
- [Spawn](src/ctmsn/scenarios/spawn/README.md)

Технические документы по сценариям:
- [FAST_SMITH_IMPLEMENTATION.md](FAST_SMITH_IMPLEMENTATION.md)
- [TIME_PROCESS_IMPLEMENTATION.md](TIME_PROCESS_IMPLEMENTATION.md)
- [FISHING_IMPLEMENTATION.md](FISHING_IMPLEMENTATION.md)
- [SPAWN_IMPLEMENTATION.md](SPAWN_IMPLEMENTATION.md)

## Тестирование

Базовые проверки ядра:

```bash
python3 tests/test_smoke_imports.py
python3 tests/test_fast_smith.py
python3 -m pytest tests/scenarios/test_fishing_builds.py
```

E2E для UI:

```bash
source venv/bin/activate
make test-e2e
```

## Документация

Основные документы:
- [USAGE.md](USAGE.md) — практическое руководство
- [FORCING_IMPLEMENTATION.md](FORCING_IMPLEMENTATION.md) — форсинг-движок
- [src/ctmsn/scenarios/README.md](src/ctmsn/scenarios/README.md) — создание сценариев
- [DOCUMENTATION_SUMMARY.md](DOCUMENTATION_SUMMARY.md) — обзор всей документации
- [NAVIGATION.md](NAVIGATION.md) — карта переходов
- [RELEASE_NOTES.md](RELEASE_NOTES.md) — история изменений документации

Быстрые маршруты:
- Новичок: `README.md` → `USAGE.md` → `src/ctmsn/examples/`
- Разработчик: `USAGE.md` → `FORCING_IMPLEMENTATION.md` → `src/ctmsn/scenarios/README.md`
- Исследователь: `FORCING_IMPLEMENTATION.md` → документы сценариев → исходный код

## Текущее состояние

| Компонент | Статус | Примечание |
|---|---|---|
| Ядро семантической сети | Реализовано | Иммутабельные структуры данных |
| Логика и TriBool | Реализовано | `TRUE/FALSE/UNKNOWN` |
| Форсинг `check/forces/force` | Реализовано частично | `force()` без полноценного поиска |
| Сценарии `fast_smith/time_process/fishing/spawn` | Реализовано | Есть демо и тесты сценариев |
| Локальный UI (API + Web) | Реализовано | Редакторы, forcing-панель, auth, teacher |

---

Лицензирование проекта описывается в настройках пакета и репозитории.

> **Навигация:** **Вы здесь: Главная** | [Руководство пользователя →](USAGE.md) | [Карта документации →](NAVIGATION.md)

# CTMSN - Composable Typed Modules for Semantic Networks

> **Навигация:** **Вы здесь: Главная** | [Руководство пользователя →](USAGE.md) | [Карта документации →](NAVIGATION.md)

CTMSN — исследовательская платформа на Python для работы с семантическими сетями, параметризацией,
форсингом и **композиционной вычислительной моделью с переходными/устойчивыми режимами**.
Ядро библиотеки (`src/ctmsn`) использует только стандартную библиотеку Python (zero-dependency);
внешние зависимости изолированы в опциональных модулях через extras (`experiment`, `io`).

Платформа реализует исследовательский трек по теме диссертации (см. [docs/ROADMAP-ASP.md](docs/ROADMAP-ASP.md)):
управляющий граф с переходными/устойчивыми режимами, экспериментальный контур с метриками,
сравнение с baseline и статистикой, декларативный DSL моделей и формальную верификацию.

## 📖 Содержание
- [Что в проекте](#что-в-проекте)
- [Быстрый старт (ядро)](#быстрый-старт-ядро)
- [Переходы, эксперименты, верификация](#переходы-эксперименты-верификация)
- [Локальный UI (API + Web)](#локальный-ui-api--web)
- [Развёртывание (Docker)](#развёртывание-docker)
- [Структура проекта](#структура-проекта)
- [Сценарии и лабораторные работы](#сценарии-и-лабораторные-работы)
- [Тестирование и CI](#тестирование-и-ci)
- [Документация](#документация)
- [Текущее состояние](#текущее-состояние)

## Что в проекте
- Семантическая сеть: `Concept`, `Predicate`, `Statement`, `SemanticNetwork`
- Параметризация: `Domain`, `Variable`, `Context`
- Логика: `FactAtom`, `EqAtom`, `Not`, `And`, `Or`, `Implies`, `TriBool`
- Форсинг: `ForcingEngine.check()`, `ForcingEngine.forces()`, `ForcingEngine.force()` с `BruteEnumStrategy`
- **Переходные/устойчивые режимы** (`transition/`): `TransitionEngine`, правила переходов (гвард + эффект), инварианты, структурированная трасса, классификация режима (transient/stable), метрика сходимости
- **Ограниченный model-checker** (`transition/model_check.py`): исчерпывающий обход достижимых состояний, проверка инвариантов, контрпример
- **Экспериментальный контур** (`experiment/`): метрики (Convergence Time, Constraint Satisfaction Rate и др.), batch-прогон, экспорт JSON/CSV
- **Сравнение baseline A/B/C + статистика** (`experiment/baselines`, `experiment/stats.py`): Mann–Whitney, bootstrap CI (extras `experiment`)
- **Декларативный DSL моделей** (`io/`): описание сети + правил + инвариантов в JSON/YAML, round-trip `load/dump_model` (YAML — extras `io`)
- **Формальная верификация** (`specs/`): TLA+-спецификация + конфигурации TLC
- Сценарии: `fast_smith`, `time_process`, `fishing`, `spawn`, `lab1_university`, `lab3_formulas`, `lab5_inheritance`
- Веб-приложение: `apps/api` (FastAPI), `apps/web` (Next.js)
- Панель преподавателя: просмотр workspace студентов, оценки, комментарии
- Система баг-репортов: отправка, скриншоты, управление статусами
- Справочная система: глоссарий, таблицы истинности, описания заданий
- Развёртывание: Docker Compose, Nginx, Let's Encrypt, Ansible

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

## Переходы, эксперименты, верификация

Ядро остаётся zero-dependency; для статистики и YAML установите extras:

```bash
pip3 install -e '.[experiment,io]'   # numpy/scipy/statsmodels, PyYAML
```

Демонстрации исследовательского контура:

```bash
python3 src/ctmsn/examples/transition_demo.py          # переходные → устойчивый режим, трасса
python3 src/ctmsn/examples/verify_demo.py              # ограниченный model-checker (инвариант + контрпример)
python3 src/ctmsn/examples/dsl_demo.py                 # загрузка модели из JSON/YAML, round-trip
python3 src/ctmsn/examples/experiment_demo.py          # batch-метрики (Convergence Time, CSR, ...)
python3 src/ctmsn/examples/baseline_comparison_demo.py # baseline A/B/C + Mann–Whitney + bootstrap CI (extras experiment)
python3 src/ctmsn/examples/doc_workflow_demo.py        # витринный сценарий: все доработки в одном потоке
```

Краткие API:

```python
from ctmsn.transition import TransitionEngine, TransitionRule, AddFact, RetractFact, invariants, make_state, check_model
from ctmsn.io import load_model, dump_model, loads_model_json   # декларативный DSL моделей
from ctmsn.experiment import run_suite, staged_process_case      # batch-метрики
```

Формальная верификация (TLA+) — опционально, требует Java и `tla2tools.jar`:

```bash
specs/check.sh                      # корректная конфигурация (все свойства)
specs/check.sh Transition_leaky.cfg # дефектная: TLC находит нарушение Consistency
```

Подробнее: [docs/VERIFICATION.md](docs/VERIFICATION.md), [docs/ROADMAP-ASP.md](docs/ROADMAP-ASP.md).

## Локальный UI (API + Web)

```bash
source venv/bin/activate
make install
make dev
```

Сервисы после запуска:
- Web: `http://localhost:3000`
- API: `http://127.0.0.1:8000`

Возможности веб-интерфейса:
- Редактирование семантической сети (концепты, предикаты, факты)
- Редактор переменных и контекстов
- Конструктор формул с вычислением в трёхзначной логике
- Форсинг-панель: `check`, `forces`, `force` с отображением расширенного контекста
- Панель переходов: редактор правил (гвард + эффект add/retract), выбор инвариантов, запуск, пошаговая трасса и подсветка затронутых узлов на графе
- Панель статистики сети (концепты, предикаты, факты, уравнения)
- Визуализация графа с ID концептов на узлах
- Справочная панель с глоссарием и таблицами истинности
- Панель преподавателя: список студентов, просмотр workspace (read-only), оценки, комментарии
- Система баг-репортов: форма отправки со скриншотами, панель управления для преподавателя

См. также:
- [apps/api/README.md](apps/api/README.md)
- [apps/web/README.md](apps/web/README.md)
- [UI_IMPLEMENTATION.md](UI_IMPLEMENTATION.md)

## Развёртывание (Docker)

Проект включает готовую конфигурацию для развёртывания на сервере:

```bash
docker compose up -d --build
```

Компоненты:
- **api** — FastAPI-сервер (Python 3.11, Uvicorn)
- **web** — Next.js в standalone-режиме (Node 20)
- **nginx** — reverse proxy с SSL (Let's Encrypt)
- **certbot** — автоматическое обновление сертификатов

Автоматизация через Ansible:

```bash
cd deploy/ansible
ansible-playbook -i hosts playbook.yml
```

Подробнее: `docker-compose.yml`, `deploy/setup.sh`, `deploy/ansible/playbook.yml`

## Структура проекта

```text
src/ctmsn/
├── core/        # Примитивы семантической сети (+ SemanticNetwork.copy)
├── param/       # Домены, переменные, контексты
├── logic/       # Формулы, термы, TriBool, evaluator
├── forcing/     # ForcingEngine, conditions, result, strategy (BruteEnumStrategy)
├── transition/  # Переходы: engine, rule, invariant, trace, model_check (zero-dep)
├── experiment/  # Метрики, batch-runner, report; baselines/ + stats.py (extras)
├── io/          # Сериализация + DSL: serializer, formula_io, transition_io, model
├── scenarios/   # fast_smith, time_process, fishing, spawn, lab1_university, lab3_formulas, lab5_inheritance
└── examples/    # hello_forcing и демо (transition/experiment/verify/dsl/baseline)

specs/           # TLA+: Transition.tla, *.cfg, check.sh (опциональная проверка TLC)

apps/
├── api/         # FastAPI backend (auth, workspaces, editors, transition, teacher, bugs)
└── web/         # Next.js frontend (редакторы, граф, форсинг, переходы, оценки, справка)

deploy/
├── ansible/     # Ansible playbook для автоматического развёртывания
├── nginx.conf   # Конфигурация Nginx с SSL
├── setup.sh     # Скрипт начальной настройки сервера
└── renew-certs.sh

docs/
├── ROADMAP-ASP.md             # дорожная карта исследовательской платформы (S1–S6)
├── VERIFICATION.md            # формальная верификация (TLA+ + model-checker)
├── LAB1_UNIVERSITY_INSTRUCTION.md
├── LAB2_SCENARIOS_INSTRUCTION.md
├── LAB3_FORMULAS_INSTRUCTION.md
└── LAB4_FORCING_INSTRUCTION.md

.github/workflows/ci.yml       # CI: ruff, mypy, pytest, smoke-демо, tsc (web)

tests/
├── test_*.py    # ядро, переходы, эксперименты, baseline, статистика, io round-trip, верификация
└── e2e_*.py     # end-to-end тесты UI (Playwright), включая e2e_transition
```

## Сценарии и лабораторные работы

### Сценарии

Реализованные сценарии:
- [Fast Smith](src/ctmsn/scenarios/fast_smith/README.md)
- [Time Process](src/ctmsn/scenarios/time_process/README.md)
- [Fishing](src/ctmsn/scenarios/fishing/README.md)
- [Spawn](src/ctmsn/scenarios/spawn/README.md)
- [Lab1 University](src/ctmsn/scenarios/lab1_university/README.md)
- [Doc Workflow](src/ctmsn/scenarios/doc_workflow/README.md) — витринный сценарий со всеми доработками платформы (переходы, инварианты, верификация, метрики, DSL)

Технические документы по сценариям:
- [FAST_SMITH_IMPLEMENTATION.md](FAST_SMITH_IMPLEMENTATION.md)
- [TIME_PROCESS_IMPLEMENTATION.md](TIME_PROCESS_IMPLEMENTATION.md)
- [FISHING_IMPLEMENTATION.md](FISHING_IMPLEMENTATION.md)
- [SPAWN_IMPLEMENTATION.md](SPAWN_IMPLEMENTATION.md)

### Лабораторные работы

Инструкции для выполнения лабораторных работ:

| Лабораторная | Тема | Инструкция |
|---|---|---|
| ЛР 1 | Построение семантической сети | [LAB1_UNIVERSITY_INSTRUCTION.md](docs/LAB1_UNIVERSITY_INSTRUCTION.md) |
| ЛР 2 | Анализ сценариев (композиция, уравнения) | [LAB2_SCENARIOS_INSTRUCTION.md](docs/LAB2_SCENARIOS_INSTRUCTION.md) |
| ЛР 3 | Формулы и трёхзначная логика | [LAB3_FORMULAS_INSTRUCTION.md](docs/LAB3_FORMULAS_INSTRUCTION.md) |
| ЛР 4 | Параметризация, условия, форсинг | [LAB4_FORCING_INSTRUCTION.md](docs/LAB4_FORCING_INSTRUCTION.md) |
| ЛР 5 | Наследование и исключения | [LAB5_INHERITANCE_INSTRUCTION.md](docs/LAB5_INHERITANCE_INSTRUCTION.md) |
| ЛР 6 | Переходы, верификация, метрики | [LAB6_WORKFLOW_INSTRUCTION.md](docs/LAB6_WORKFLOW_INSTRUCTION.md) |

## Тестирование и CI

Модульные тесты (ядро, переходы, эксперименты, baseline, статистика, io, верификация):

```bash
pip3 install -e '.[experiment,io,dev]'
pytest --ignore=tests/test_network_from_json_contradictions.py -q
```

Отдельные проверки:

```bash
python3 -m pytest tests/test_transition_engine.py     # переходные/устойчивые режимы
python3 -m pytest tests/test_spec_conformance.py      # ограниченный model-checker
python3 -m pytest tests/test_experiment.py tests/test_baselines.py tests/test_stats.py
python3 -m pytest tests/test_io_roundtrip.py          # round-trip DSL моделей
```

Линт и типизация:

```bash
ruff check src/ctmsn      # конфигурация в pyproject.toml
mypy                      # строго для модулей transition/experiment/io
```

E2E для UI (Playwright):

```bash
source venv/bin/activate
make test-e2e
```

CI (GitHub Actions, `.github/workflows/ci.yml`) на каждый push/PR в `main`:
ruff → mypy → pytest → smoke-прогон демо (job python) и `tsc --noEmit` (job web).

## Документация

Основные документы:
- [docs/THEORY.md](docs/THEORY.md) — формальная и теоретическая модель (определения, семантика, верификация; для диссертации)
- [docs/ROADMAP-ASP.md](docs/ROADMAP-ASP.md) — дорожная карта исследовательской платформы (S1–S6)
- [docs/VERIFICATION.md](docs/VERIFICATION.md) — формальная верификация (TLA+ + ограниченный model-checker)
- [USAGE.md](USAGE.md) — практическое руководство
- [FORCING_IMPLEMENTATION.md](FORCING_IMPLEMENTATION.md) — форсинг-движок
- [src/ctmsn/scenarios/README.md](src/ctmsn/scenarios/README.md) — создание сценариев
- [DOCUMENTATION_SUMMARY.md](DOCUMENTATION_SUMMARY.md) — обзор всей документации
- [NAVIGATION.md](NAVIGATION.md) — карта переходов
- [RELEASE_NOTES.md](RELEASE_NOTES.md) — история изменений документации

Инструкции к лабораторным работам:
- [docs/LAB1_UNIVERSITY_INSTRUCTION.md](docs/LAB1_UNIVERSITY_INSTRUCTION.md)
- [docs/LAB2_SCENARIOS_INSTRUCTION.md](docs/LAB2_SCENARIOS_INSTRUCTION.md)
- [docs/LAB3_FORMULAS_INSTRUCTION.md](docs/LAB3_FORMULAS_INSTRUCTION.md)
- [docs/LAB4_FORCING_INSTRUCTION.md](docs/LAB4_FORCING_INSTRUCTION.md)
- [docs/LAB5_INHERITANCE_INSTRUCTION.md](docs/LAB5_INHERITANCE_INSTRUCTION.md)
- [docs/LAB6_WORKFLOW_INSTRUCTION.md](docs/LAB6_WORKFLOW_INSTRUCTION.md)

Быстрые маршруты:
- Новичок: `README.md` → `USAGE.md` → `src/ctmsn/examples/`
- Разработчик: `USAGE.md` → `FORCING_IMPLEMENTATION.md` → `src/ctmsn/scenarios/README.md`
- Исследователь: `FORCING_IMPLEMENTATION.md` → документы сценариев → исходный код
- Студент: `docs/LAB1_UNIVERSITY_INSTRUCTION.md` → `LAB2` → `LAB3` → `LAB4`

## Текущее состояние

| Компонент | Статус | Примечание |
|---|---|---|
| Ядро семантической сети | Реализовано | Иммутабельные структуры данных |
| Логика и TriBool | Реализовано | `TRUE/FALSE/UNKNOWN` |
| Форсинг `check/forces` | Реализовано | Проверка условий и вынуждение формул |
| Форсинг `force` (поиск) | Реализовано | `BruteEnumStrategy` с ограничением пространства поиска |
| Переходные/устойчивые режимы (S1) | Реализовано | `TransitionEngine`, правила, инварианты, трасса, API + панель UI |
| Экспериментальный контур (S2) | Реализовано | Метрики, batch-runner, экспорт JSON/CSV |
| Baseline A/B/C + статистика (S3) | Реализовано | Mann–Whitney, bootstrap CI (extras `experiment`) |
| DSL загрузки моделей (S4) | Реализовано | JSON/YAML, round-trip `load/dump_model` (YAML — extras `io`) |
| Формальная верификация (S5) | Реализовано | TLA+-спецификация + ограниченный model-checker |
| CI/CD (S6) | Реализовано | GitHub Actions: ruff, mypy, pytest, tsc |
| Сценарии | Реализовано | `fast_smith`, `time_process`, `fishing`, `spawn`, `lab1_university`, `lab3_formulas`, `lab5_inheritance` |
| Лабораторные работы | Реализовано | 4 лабораторные с инструкциями |
| Локальный UI (API + Web) | Реализовано | Редакторы, форсинг- и переход-панели, auth, справка |
| Панель преподавателя | Реализовано | Просмотр workspace (read-only), оценки, комментарии |
| Система баг-репортов | Реализовано | Отправка, скриншоты, управление статусами |
| Развёртывание | Реализовано | Docker Compose, Nginx, SSL, Ansible |

---

Лицензирование проекта описывается в настройках пакета и репозитория.

> **Навигация:** **Вы здесь: Главная** | [Руководство пользователя →](USAGE.md) | [Карта документации →](NAVIGATION.md)

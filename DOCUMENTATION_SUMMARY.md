# Сводка документации CTMSN

> **Навигация:** [🏠 Главная](README.md) | [Карта документации ←](NAVIGATION.md) | **Вы здесь: Сводка документации** | [История изменений →](RELEASE_NOTES.md)

## Обзор

Документация покрывает четыре области проекта:
- ядро библиотеки (`src/ctmsn`)
- исследовательская платформа: переходы, эксперименты, верификация (`transition`, `experiment`, `io`, `specs`)
- локальное приложение (`apps/api`, `apps/web`)
- инструкции к лабораторным работам (`docs/`)

## Основные документы

| Документ | Область |
|---|---|
| [README.md](README.md) | Общий вход, структура, команды запуска |
| [docs/THEORY.md](docs/THEORY.md) | Формальная и теоретическая модель (определения, семантика, верификация) |
| [docs/ROADMAP-ASP.md](docs/ROADMAP-ASP.md) | Дорожная карта исследовательской платформы (S1–S6) |
| [docs/VERIFICATION.md](docs/VERIFICATION.md) | Формальная верификация: TLA+ и ограниченный model-checker |
| [USAGE.md](USAGE.md) | Практическое использование API ядра |
| [FORCING_IMPLEMENTATION.md](FORCING_IMPLEMENTATION.md) | Формальная и техническая часть форсинга |
| [src/ctmsn/scenarios/README.md](src/ctmsn/scenarios/README.md) | Шаблон и правила создания сценариев |
| [apps/api/README.md](apps/api/README.md) | Локальный FastAPI backend |
| [apps/web/README.md](apps/web/README.md) | Локальный Next.js frontend |
| [UI_IMPLEMENTATION.md](UI_IMPLEMENTATION.md) | Архитектура и функциональные блоки UI |
| [NAVIGATION.md](NAVIGATION.md) | Маршруты чтения по документации |
| [RELEASE_NOTES.md](RELEASE_NOTES.md) | Журнал изменений документации |

## Инструкции к лабораторным работам

| Документ | Тема |
|---|---|
| [docs/LAB1_UNIVERSITY_INSTRUCTION.md](docs/LAB1_UNIVERSITY_INSTRUCTION.md) | Построение семантической сети |
| [docs/LAB2_SCENARIOS_INSTRUCTION.md](docs/LAB2_SCENARIOS_INSTRUCTION.md) | Анализ сценариев (композиция, уравнения) |
| [docs/LAB3_FORMULAS_INSTRUCTION.md](docs/LAB3_FORMULAS_INSTRUCTION.md) | Формулы и трёхзначная логика |
| [docs/LAB4_FORCING_INSTRUCTION.md](docs/LAB4_FORCING_INSTRUCTION.md) | Параметризация, условия, форсинг |
| [docs/LAB5_INHERITANCE_INSTRUCTION.md](docs/LAB5_INHERITANCE_INSTRUCTION.md) | Наследование и исключения |
| [docs/LAB6_WORKFLOW_INSTRUCTION.md](docs/LAB6_WORKFLOW_INSTRUCTION.md) | Переходы, верификация, метрики (сценарий doc_workflow) |

## Документы сценариев

- [FAST_SMITH_IMPLEMENTATION.md](FAST_SMITH_IMPLEMENTATION.md)
- [TIME_PROCESS_IMPLEMENTATION.md](TIME_PROCESS_IMPLEMENTATION.md)
- [FISHING_IMPLEMENTATION.md](FISHING_IMPLEMENTATION.md)
- [SPAWN_IMPLEMENTATION.md](SPAWN_IMPLEMENTATION.md)
- `src/ctmsn/scenarios/*/README.md`

## Рекомендованный порядок чтения

### Библиотека
1. [README.md](README.md)
2. [USAGE.md](USAGE.md)
3. [FORCING_IMPLEMENTATION.md](FORCING_IMPLEMENTATION.md)
4. документы сценариев

### Исследовательская платформа
1. [docs/ROADMAP-ASP.md](docs/ROADMAP-ASP.md)
2. `src/ctmsn/transition/` + `src/ctmsn/examples/transition_demo.py`
3. `src/ctmsn/experiment/` + `baseline_comparison_demo.py`
4. [docs/VERIFICATION.md](docs/VERIFICATION.md) + `specs/`

### Теоретическая модель (диссертация)
1. [docs/THEORY.md](docs/THEORY.md)
2. [docs/VERIFICATION.md](docs/VERIFICATION.md)
3. [docs/deep-research-report-asp.md](docs/deep-research-report-asp.md)

### UI/API
1. [README.md](README.md#локальный-ui-api--web)
2. [UI_IMPLEMENTATION.md](UI_IMPLEMENTATION.md)
3. [apps/api/README.md](apps/api/README.md)
4. [apps/web/README.md](apps/web/README.md)
5. `tests/e2e_*.py`

### Студент (лабораторные)
1. [docs/LAB1_UNIVERSITY_INSTRUCTION.md](docs/LAB1_UNIVERSITY_INSTRUCTION.md)
2. [docs/LAB2_SCENARIOS_INSTRUCTION.md](docs/LAB2_SCENARIOS_INSTRUCTION.md)
3. [docs/LAB3_FORMULAS_INSTRUCTION.md](docs/LAB3_FORMULAS_INSTRUCTION.md)
4. [docs/LAB4_FORCING_INSTRUCTION.md](docs/LAB4_FORCING_INSTRUCTION.md)

## Покрытие по темам

- Семантическая сеть, параметризация, логика, форсинг
- Переходные/устойчивые режимы: правила, инварианты, трасса, model-checker
- Экспериментальный контур: метрики, batch-прогон, экспорт артефактов
- Сравнение baseline A/B/C и статистика (Mann–Whitney, bootstrap CI)
- Декларативный DSL моделей (JSON/YAML), round-trip
- Формальная верификация: TLA+-спецификация и ограниченный model-checker
- Сценарии: `fast_smith`, `time_process`, `fishing`, `spawn`, `lab1_university`, `lab3_formulas`, `lab5_inheritance`, `doc_workflow`
- Запуск и сопровождение локального UI (включая панель переходов)
- Панель преподавателя: просмотр workspace, оценки, комментарии
- Система баг-репортов: отправка, управление статусами
- Справочная система: глоссарий, таблицы истинности
- Развёртывание: Docker Compose, Nginx, Ansible
- Качество: ruff, mypy, pytest, CI (GitHub Actions); базовые/юнит/e2e-тесты

---

> **Навигация:** [🏠 Главная](README.md) | [Карта документации ←](NAVIGATION.md) | **Вы здесь: Сводка документации** | [История изменений →](RELEASE_NOTES.md)

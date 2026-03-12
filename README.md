# CTMSN - Composable Typed Modules for Semantic Networks

> **Навигация:** **Вы здесь: Главная** | [Руководство пользователя →](USAGE.md) | [Карта документации →](NAVIGATION.md)

CTMSN — библиотека на Python для работы с семантическими сетями, параметризацией и форсингом.  
Ядро библиотеки (`src/ctmsn`) использует только стандартную библиотеку Python.

## 📖 Содержание
- [Что в проекте](#что-в-проекте)
- [Быстрый старт (ядро)](#быстрый-старт-ядро)
- [Локальный UI (API + Web)](#локальный-ui-api--web)
- [Развёртывание (Docker)](#развёртывание-docker)
- [Структура проекта](#структура-проекта)
- [Сценарии и лабораторные работы](#сценарии-и-лабораторные-работы)
- [Тестирование](#тестирование)
- [Документация](#документация)
- [Текущее состояние](#текущее-состояние)

## Что в проекте
- Семантическая сеть: `Concept`, `Predicate`, `Statement`, `SemanticNetwork`
- Параметризация: `Domain`, `Variable`, `Context`
- Логика: `FactAtom`, `EqAtom`, `Not`, `And`, `Or`, `Implies`, `TriBool`
- Форсинг: `ForcingEngine.check()`, `ForcingEngine.forces()`, `ForcingEngine.force()` с `BruteEnumStrategy`
- Сценарии: `fast_smith`, `time_process`, `fishing`, `spawn`, `lab1_university`, `lab3_formulas`
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
├── core/        # Примитивы семантической сети
├── param/       # Домены, переменные, контексты
├── logic/       # Формулы, термы, TriBool, evaluator
├── forcing/     # ForcingEngine, conditions, result, strategy (BruteEnumStrategy)
├── scenarios/   # fast_smith, time_process, fishing, spawn, lab1_university, lab3_formulas
├── examples/    # hello_forcing и демо-сценарии
└── io/          # сериализация

apps/
├── api/         # FastAPI backend (auth, workspaces, editors, teacher, bugs)
└── web/         # Next.js frontend (редакторы, граф, форсинг, оценки, справка)

deploy/
├── ansible/     # Ansible playbook для автоматического развёртывания
├── nginx.conf   # Конфигурация Nginx с SSL
├── setup.sh     # Скрипт начальной настройки сервера
└── renew-certs.sh

docs/
├── LAB1_UNIVERSITY_INSTRUCTION.md
├── LAB2_SCENARIOS_INSTRUCTION.md
├── LAB3_FORMULAS_INSTRUCTION.md
└── LAB4_FORCING_INSTRUCTION.md

tests/
├── test_*.py    # базовые проверки ядра и force()-поиска
└── e2e_*.py     # end-to-end тесты UI (Playwright)
```

## Сценарии и лабораторные работы

### Сценарии

Реализованные сценарии:
- [Fast Smith](src/ctmsn/scenarios/fast_smith/README.md)
- [Time Process](src/ctmsn/scenarios/time_process/README.md)
- [Fishing](src/ctmsn/scenarios/fishing/README.md)
- [Spawn](src/ctmsn/scenarios/spawn/README.md)
- [Lab1 University](src/ctmsn/scenarios/lab1_university/README.md)

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

## Тестирование

Базовые проверки ядра:

```bash
python3 tests/test_smoke_imports.py
python3 tests/test_fast_smith.py
python3 tests/test_force_search.py
python3 -m pytest tests/scenarios/test_fishing_builds.py
```

E2E для UI (Playwright):

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

Инструкции к лабораторным работам:
- [docs/LAB1_UNIVERSITY_INSTRUCTION.md](docs/LAB1_UNIVERSITY_INSTRUCTION.md)
- [docs/LAB2_SCENARIOS_INSTRUCTION.md](docs/LAB2_SCENARIOS_INSTRUCTION.md)
- [docs/LAB3_FORMULAS_INSTRUCTION.md](docs/LAB3_FORMULAS_INSTRUCTION.md)
- [docs/LAB4_FORCING_INSTRUCTION.md](docs/LAB4_FORCING_INSTRUCTION.md)

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
| Сценарии | Реализовано | `fast_smith`, `time_process`, `fishing`, `spawn`, `lab1_university`, `lab3_formulas` |
| Лабораторные работы | Реализовано | 4 лабораторные с инструкциями |
| Локальный UI (API + Web) | Реализовано | Редакторы, форсинг-панель, auth, справка |
| Панель преподавателя | Реализовано | Просмотр workspace (read-only), оценки, комментарии |
| Система баг-репортов | Реализовано | Отправка, скриншоты, управление статусами |
| Развёртывание | Реализовано | Docker Compose, Nginx, SSL, Ansible |

---

Лицензирование проекта описывается в настройках пакета и репозитория.

> **Навигация:** **Вы здесь: Главная** | [Руководство пользователя →](USAGE.md) | [Карта документации →](NAVIGATION.md)

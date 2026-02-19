# Карта навигации документации CTMSN

> **Навигация:** [🏠 Главная](README.md) | **Вы здесь: Карта документации** | [Сводка документации →](DOCUMENTATION_SUMMARY.md)

## 📖 Содержание
- [Быстрые маршруты](#быстрые-маршруты)
- [Полный граф документов](#полный-граф-документов)
- [Справочная таблица](#справочная-таблица)
- [Навигация по задачам](#навигация-по-задачам)

## Быстрые маршруты

### Новичок
`README.md` → `USAGE.md` → `src/ctmsn/examples/` → `src/ctmsn/scenarios/fast_smith/README.md`

### Разработчик
`USAGE.md` → `FORCING_IMPLEMENTATION.md` → `src/ctmsn/scenarios/README.md` → документы сценариев

### Исследователь
`FORCING_IMPLEMENTATION.md` → `*_IMPLEMENTATION.md` → исходный код в `src/ctmsn/`

### UI/API разработка
`README.md` → `apps/api/README.md` + `apps/web/README.md` → `tests/e2e_*.py`

## Полный граф документов

```text
README.md
├─ USAGE.md
│  ├─ FORCING_IMPLEMENTATION.md
│  ├─ src/ctmsn/scenarios/README.md
│  └─ src/ctmsn/examples/*
├─ NAVIGATION.md
├─ DOCUMENTATION_SUMMARY.md
├─ RELEASE_NOTES.md
├─ apps/api/README.md
├─ apps/web/README.md
├─ UI_IMPLEMENTATION.md
├─ FAST_SMITH_IMPLEMENTATION.md
├─ TIME_PROCESS_IMPLEMENTATION.md
├─ FISHING_IMPLEMENTATION.md
└─ SPAWN_IMPLEMENTATION.md
```

## Справочная таблица

| Документ | Назначение |
|---|---|
| [README.md](README.md) | Точка входа и обзор |
| [USAGE.md](USAGE.md) | Практическое использование библиотеки |
| [FORCING_IMPLEMENTATION.md](FORCING_IMPLEMENTATION.md) | Детали логики форсинга |
| [src/ctmsn/scenarios/README.md](src/ctmsn/scenarios/README.md) | Шаблон создания сценариев |
| [FAST_SMITH_IMPLEMENTATION.md](FAST_SMITH_IMPLEMENTATION.md) | Реализация Fast Smith |
| [TIME_PROCESS_IMPLEMENTATION.md](TIME_PROCESS_IMPLEMENTATION.md) | Реализация Time Process |
| [FISHING_IMPLEMENTATION.md](FISHING_IMPLEMENTATION.md) | Реализация Fishing |
| [SPAWN_IMPLEMENTATION.md](SPAWN_IMPLEMENTATION.md) | Реализация Spawn |
| [apps/api/README.md](apps/api/README.md) | Локальный API сервер |
| [apps/web/README.md](apps/web/README.md) | Локальный Web клиент |
| [DOCUMENTATION_SUMMARY.md](DOCUMENTATION_SUMMARY.md) | Сводка и покрытие |
| [RELEASE_NOTES.md](RELEASE_NOTES.md) | История изменений документации |

## Навигация по задачам

- Начать с нуля: [README.md](README.md#быстрый-старт-ядро)
- Разобраться с API ядра: [USAGE.md](USAGE.md#ключевые-api)
- Изучить алгоритм форсинга: [FORCING_IMPLEMENTATION.md](FORCING_IMPLEMENTATION.md)
- Запустить готовый сценарий: [src/ctmsn/scenarios/fast_smith/README.md](src/ctmsn/scenarios/fast_smith/README.md)
- Собрать собственный сценарий: [src/ctmsn/scenarios/README.md](src/ctmsn/scenarios/README.md)
- Работать с локальным UI: [apps/api/README.md](apps/api/README.md), [apps/web/README.md](apps/web/README.md)

---

> **Навигация:** [🏠 Главная](README.md) | **Вы здесь: Карта документации** | [Сводка документации →](DOCUMENTATION_SUMMARY.md)

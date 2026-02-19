# Сводка документации CTMSN

> **Навигация:** [🏠 Главная](README.md) | [Карта документации ←](NAVIGATION.md) | **Вы здесь: Сводка документации** | [История изменений →](RELEASE_NOTES.md)

## Обзор

Документация покрывает две области проекта:
- ядро библиотеки (`src/ctmsn`)
- локальное приложение (`apps/api`, `apps/web`)

## Основные документы

| Документ | Область |
|---|---|
| [README.md](README.md) | Общий вход, структура, команды запуска |
| [USAGE.md](USAGE.md) | Практическое использование API ядра |
| [FORCING_IMPLEMENTATION.md](FORCING_IMPLEMENTATION.md) | Формальная и техническая часть форсинга |
| [src/ctmsn/scenarios/README.md](src/ctmsn/scenarios/README.md) | Шаблон и правила создания сценариев |
| [apps/api/README.md](apps/api/README.md) | Локальный FastAPI backend |
| [apps/web/README.md](apps/web/README.md) | Локальный Next.js frontend |
| [NAVIGATION.md](NAVIGATION.md) | Маршруты чтения по документации |
| [RELEASE_NOTES.md](RELEASE_NOTES.md) | Журнал изменений документации |

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

### UI/API
1. [README.md](README.md#локальный-ui-api--web)
2. [apps/api/README.md](apps/api/README.md)
3. [apps/web/README.md](apps/web/README.md)
4. `tests/e2e_*.py`

## Покрытие по темам

- Семантическая сеть, параметризация, логика, форсинг
- Сценарии: `fast_smith`, `time_process`, `fishing`, `spawn`
- Запуск и сопровождение локального UI
- Базовые тесты и e2e-проверки

---

> **Навигация:** [🏠 Главная](README.md) | [Карта документации ←](NAVIGATION.md) | **Вы здесь: Сводка документации** | [История изменений →](RELEASE_NOTES.md)

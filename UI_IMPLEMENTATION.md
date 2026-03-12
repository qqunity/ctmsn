# UI Implementation

> **Навигация:** [🏠 Главная](README.md) | **Вы здесь: UI Implementation** | [apps/api/README.md →](apps/api/README.md)

Локальный UI включает backend на FastAPI и frontend на Next.js для интерактивной работы с семантическими сетями, контекстами, формулами и форсингом.

## 📖 Содержание
- [Архитектура](#архитектура)
- [Запуск](#запуск)
- [Функциональные блоки UI](#функциональные-блоки-ui)
- [API-контур](#api-контур)
- [Структура приложений](#структура-приложений)
- [Тестирование](#тестирование)
- [Troubleshooting](#troubleshooting)

## Архитектура

- `apps/api` — FastAPI API, хранение workspace-состояний, auth, teacher-функции, баг-репорты, оценки
- `apps/web` — Next.js клиент, графовая визуализация, редакторы сущностей, формул, переменных и контекстов, форсинг-панель, справочная система
- `src/ctmsn` — библиотечное ядро (сценарии, логика, форсинг)

## Запуск

```bash
source venv/bin/activate
make install
make dev
```

Адреса:
- Web: `http://localhost:3000`
- API: `http://127.0.0.1:8000`

Раздельный запуск:

```bash
source venv/bin/activate
make dev-api
make dev-web
```

## Функциональные блоки UI

### Аутентификация и роли
- Регистрация/вход пользователя
- Обновление токена
- Роль преподавателя (`teacher`) с доступом к студенческим workspace

### Рабочие пространства
- Создание из сценария или «чистого листа»
- Переименование, дублирование, удаление
- Экспорт/импорт
- История изменений (`undo/redo`)

### Редакторы
- Граф: концепты, предикаты, факты; ID концептов отображаются на узлах
- Формулы: CRUD и вычисление в трёхзначной логике
- Переменные: CRUD, домены, возможность сброса присвоенного значения
- Контексты: CRUD, активация, сравнение, highlights
- Панель forcing: `check`, `forces`, `force` с отображением расширенного контекста

### Панель статистики сети
- Количество концептов, предикатов, фактов, уравнений

### Справочная система
- Описания заданий для каждого сценария
- Глоссарий (Концепт, Предикат, Факт, Домен, Переменная, Контекст, Формула, Форсинг)
- Таблицы истинности для трёхзначной логики (NOT, AND, OR, IMPLIES)
- Подсказки для элементов интерфейса

### Панель преподавателя
- Список студентов с количеством workspace
- Просмотр workspace студента (read-only): граф, переменные, контексты, формулы, форсинг, уравнения
- Имя workspace вместо сценария в списке студентов
- Оценки: выставление (1–10), удаление, цветовая индикация
- Комментарии к workspace

### Система баг-репортов
- Форма отправки: заголовок, описание, привязка к workspace, загрузка скриншота
- Панель управления для преподавателя: фильтрация (все/открытые/закрытые), смена статуса, удаление, просмотр скриншотов

### Визуализация
- Граф на Cytoscape с ID концептов на узлах
- Панели статуса, деталей, формул, переменных и контекстов
- Help panel и teacher panel

## API-контур

Ключевые endpoint-группы:

- `/api/auth/*` — аутентификация
- `/api/scenarios`, `/api/session/load`, `/api/run` — сценарии и запуск
- `/api/session/*` — изменение сети и истории
- `/api/workspaces*` — управление workspace
- `/api/workspaces/{wid}/formulas*` — редактор формул
- `/api/workspaces/{wid}/variables*` — редактор переменных
- `/api/workspaces/{wid}/contexts*` — редактор контекстов
- `/api/workspaces/{wid}/forcing/*` — forcing API (`check`, `forces`, `force`)
- `/api/teacher/*` — teacher API (студенты, workspace, оценки, комментарии)
- `/api/bugs*` — баг-репорты (создание, просмотр, управление)

## Структура приложений

```text
apps/
├── api/
│   ├── Dockerfile
│   └── src/ctmsn_api/
│       ├── app.py
│       ├── config.py
│       ├── database.py
│       ├── models.py
│       ├── routes_auth.py
│       ├── routes_editors.py
│       ├── routes_teacher.py
│       ├── routes_bugs.py
│       ├── sessions.py
│       ├── registry.py
│       ├── ops.py
│       └── serialize.py
└── web/
    ├── Dockerfile
    ├── app/
    │   ├── login/page.tsx
    │   ├── register/page.tsx
    │   ├── workspaces/page.tsx
    │   ├── workspace/[id]/page.tsx
    │   └── teacher/
    │       ├── page.tsx
    │       ├── bugs/page.tsx
    │       ├── student/[id]/page.tsx
    │       └── workspace/[id]/page.tsx
    ├── components/
    │   ├── BugReportForm.tsx
    │   ├── ContextEditorPanel.tsx
    │   ├── EquationsPanel.tsx
    │   ├── ForcingPanel.tsx
    │   ├── FormulaEditorPanel.tsx
    │   ├── GradePanel.tsx
    │   ├── GraphView.tsx
    │   ├── HelpPanel.tsx
    │   ├── NetworkStatsPanel.tsx
    │   ├── ScenarioBar.tsx
    │   ├── VariableEditorPanel.tsx
    │   ├── VariablesPanel.tsx
    │   └── WorkspaceList.tsx
    └── lib/
        ├── api.ts
        ├── helpContent.ts
        └── types.ts
```

## Тестирование

UI покрывается e2e-набором:

```bash
source venv/bin/activate
make test-e2e
```

Примеры:
- `tests/e2e_auth.py`
- `tests/e2e_workspace_mgmt.py`
- `tests/e2e_network_editor.py`
- `tests/e2e_forcing.py`
- `tests/e2e_forcing_scenario_results.py`
- `tests/e2e_editors.py`
- `tests/e2e_help_panel.py`
- `tests/e2e_help_panel_scenario.py`
- `tests/e2e_teacher.py`
- `tests/e2e_teacher_readonly_workspace.py`
- `tests/e2e_teacher_workspace_names.py`
- `tests/e2e_grades.py`
- `tests/e2e_grade_display.py`
- `tests/e2e_bug_reports.py`
- `tests/e2e_lab1_university.py`
- `tests/e2e_lab2.py`
- `tests/e2e_lab3_formulas.py`
- `tests/e2e_unset_variable.py`
- `tests/e2e_graph_labels_panel.py`

## Troubleshooting

### API не поднимается
- активировать `venv`
- проверить установку зависимостей `make install-api`
- убедиться, что порт `8000` свободен

### Web не поднимается
- выполнить `make install-web`
- проверить, что `npm` доступен
- убедиться, что порт `3000` свободен

### UI не видит API
- проверить `NEXT_PUBLIC_API_BASE` в `apps/web/.env.local`
- проверить `GET /api/scenarios` на `127.0.0.1:8000`

---

> **См. также:**
> - [README.md](README.md)
> - [apps/api/README.md](apps/api/README.md)
> - [apps/web/README.md](apps/web/README.md)
> - [USAGE.md](USAGE.md)

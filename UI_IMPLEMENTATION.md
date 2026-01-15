# UI Implementation

> **Навигация:** [🏠 Главная](README.md) | **Вы здесь**

Локальный веб-интерфейс для визуализации и работы с семантическими сетями CTnSS.

## Архитектура

Монорепо с двумя приложениями:

- `apps/api` — FastAPI backend (Python 3.9+)
- `apps/web` — Next.js frontend (TypeScript + React + Tailwind)

## Быстрый старт

```bash
source venv/bin/activate
make install
make dev
```

Откройте браузер: `http://localhost:3000`

### Альтернативные способы запуска

Shell-скрипт:
```bash
source venv/bin/activate
cd apps
./run_dev.sh
```

Раздельный запуск (два терминала):

Терминал 1 (API):
```bash
source venv/bin/activate
cd apps/api
python -m pip install -r requirements.txt
PYTHONPATH=../../src python -m uvicorn ctmsn_api.app:app --reload --host 127.0.0.1 --port 8000
```

Терминал 2 (Web):
```bash
cd apps/web
npm install
npm run dev
```

## Работа с UI

### Основные действия

1. Выберите сценарий из выпадающего списка
2. Выберите режим (если доступно)
3. Включите/выключите деривацию (derive)
4. Нажмите **Load** для загрузки сценария
5. Нажмите **Run** для запуска операций

### Интерактивные возможности

- Кликните на узел/ребро графа для просмотра деталей
- Кликните на равенство в панели Equations для просмотра деталей
- Панель Status показывает результаты check/forces/force

### Цвета на графе

- Синие узлы — концепты
- Серые сплошные стрелки — базовые рёбра (edge)
- Оранжевые пунктирные стрелки — выведенные рёбра (derived_edge)

## API Endpoints

### GET /api/scenarios

Список доступных сценариев и их режимов.

```json
{
  "scenarios": [
    { "name": "fishing", "modes": [] },
    { "name": "time_process", "modes": ["sun", "prereq"] }
  ]
}
```

### POST /api/session/new

Создать новую сессию.

```json
{ "session_id": "abc123..." }
```

### POST /api/session/load

Загрузить сценарий в сессию.

**Request:**
```json
{
  "session_id": "abc123",
  "scenario": "fishing",
  "mode": null,
  "derive": true
}
```

**Response:**
```json
{
  "session_id": "string",
  "scenario": "string",
  "mode": "string | null",
  "graph": {
    "nodes": [{ "id": "string", "label": "string" }],
    "edges": [{ "id": "string", "label": "string", "source": "string", "target": "string", "kind": "edge|derived" }],
    "equations": [
      { "kind": "comp2", "left": "string", "right": "string", "result": "string" }
    ]
  },
  "check": "string",
  "forces": "string",
  "force": "string"
}
```

### POST /api/run

Запустить операции на текущей сессии.

**Request:**
```json
{
  "session_id": "abc123",
  "derive": true
}
```

**Response:** аналогично `/api/session/load`

## Структура файлов

```
apps/
├── api/
│   ├── src/ctmsn_api/
│   │   ├── app.py           # FastAPI приложение
│   │   ├── registry.py      # Регистрация сценариев
│   │   ├── sessions.py      # Управление сессиями
│   │   ├── serialize.py     # Сериализация графа
│   │   └── ops.py           # Операции check/forces/force
│   └── requirements.txt
│
└── web/
    ├── app/
    │   ├── page.tsx         # Главная страница
    │   ├── layout.tsx
    │   └── globals.css
    ├── components/
    │   ├── ScenarioBar.tsx  # Панель управления
    │   ├── GraphView.tsx    # Граф (Cytoscape)
    │   ├── StatusPanel.tsx  # Статус операций
    │   ├── EquationsPanel.tsx
    │   └── DetailsPanel.tsx
    ├── lib/
    │   ├── api.ts           # API клиент
    │   └── types.ts
    └── package.json
```

## Добавление нового сценария

1. Создайте сценарий в `src/ctmsn/scenarios/your_scenario/`
2. Добавьте регистрацию в `apps/api/src/ctmsn_api/registry.py`:

```python
try:
    from ctmsn.scenarios.your_scenario.model import build_network
    from ctmsn.scenarios.your_scenario.derive import apply
    from ctmsn.scenarios.your_scenario.goal import build_goal
    from ctmsn.scenarios.your_scenario.constraints import build_conditions
    register(ScenarioSpec("your_scenario", build_network, apply, build_goal, build_conditions))
except Exception:
    pass
```

3. Перезапустите API сервер

## Troubleshooting

### Ошибка: "Module not found: ctmsn"

Убедитесь, что PYTHONPATH указывает на `src` и venv активирован:

```bash
source venv/bin/activate
export PYTHONPATH=$(pwd)/src
```

### Ошибка: "pip: command not found"

Активируйте venv:

```bash
source venv/bin/activate
make install-api
```

### Ошибка: "Port 8000 already in use"

Остановите процесс:

```bash
make clean
```

Или:

```bash
lsof -ti:8000 | xargs kill -9
```

### Граф не отображается

1. Откройте консоль браузера (F12)
2. Проверьте, что API отвечает:
   ```bash
   curl http://127.0.0.1:8000/api/scenarios
   ```
3. Убедитесь, что сценарий загружен (панель Status должна показывать данные)

## Технологии

**Backend:**
- Python 3.9+
- FastAPI
- Uvicorn
- CTnSS (локальный пакет)

**Frontend:**
- Next.js 15
- React 19
- TypeScript 5
- Tailwind CSS 3
- Cytoscape.js

---

> **См. также:**
> - [README.md](README.md) — главная документация
> - [USAGE.md](USAGE.md) — руководство пользователя
> - [scenarios/README.md](src/ctmsn/scenarios/README.md) — создание сценариев

# CTMSN API Server

FastAPI backend для локального UI.

## Установка

```bash
source venv/bin/activate
cd apps/api
python3 -m pip install -r requirements.txt
```

## Запуск

```bash
source venv/bin/activate
cd apps/api
PYTHONPATH=../../src:src python3 -m uvicorn ctmsn_api.app:app --reload --host 127.0.0.1 --port 8000
```

Сервер: `http://127.0.0.1:8000`

## Основные группы endpoint-ов

### Сценарии и сессии
- `GET /api/scenarios`
- `POST /api/session/load`
- `POST /api/run`
- `POST /api/session/set_variable`

### Редактирование сети
- `POST /api/session/add_concept`
- `POST /api/session/add_predicate`
- `POST /api/session/add_fact`
- `POST /api/session/edit_concept`
- `POST /api/session/edit_predicate`
- `POST /api/session/remove_concept`
- `POST /api/session/remove_predicate`
- `POST /api/session/remove_fact`

### История и каскады
- `POST /api/session/{session_id}/undo`
- `POST /api/session/{session_id}/redo`
- `GET /api/session/{session_id}/history`
- `GET /api/session/{session_id}/cascade/concept/{concept_id}`
- `GET /api/session/{session_id}/cascade/predicate/{predicate_name}`

### Workspaces
- `GET /api/workspaces`
- `PATCH /api/workspaces/{workspace_id}`
- `DELETE /api/workspaces/{workspace_id}`
- `POST /api/workspaces/{workspace_id}/duplicate`
- `GET /api/workspaces/{workspace_id}/export`
- `POST /api/workspaces/import`

### Editors API
- Формулы: `/api/workspaces/{wid}/formulas*`
- Переменные: `/api/workspaces/{wid}/variables*`
- Контексты: `/api/workspaces/{wid}/contexts*`
- Форсинг: `POST /api/workspaces/{wid}/forcing/check`, `POST /api/workspaces/{wid}/forcing/forces`

### Аутентификация
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `GET /api/auth/me`

### Teacher API
- `GET /api/teacher/students`
- `GET /api/teacher/students/{student_id}/workspaces`
- `GET /api/teacher/workspaces/{workspace_id}`
- `GET|POST /api/teacher/workspaces/{workspace_id}/comments`

## Через Makefile (из корня репозитория)

```bash
source venv/bin/activate
make install-api
make dev-api
```

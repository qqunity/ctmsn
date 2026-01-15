# CTnSS API Server

FastAPI backend для локального UI.

## Установка

**Важно:** Активируйте venv перед установкой!

```bash
source venv/bin/activate

cd apps/api
python -m pip install -r requirements.txt
```

## Запуск

```bash
source venv/bin/activate

cd apps/api
PYTHONPATH=../../src python -m uvicorn ctmsn_api.app:app --reload --host 127.0.0.1 --port 8000
```

API будет доступен на `http://127.0.0.1:8000`

## Endpoints

- `GET /api/scenarios` — список доступных сценариев
- `POST /api/session/new` — создать новую сессию
- `POST /api/session/load` — загрузить сценарий
- `POST /api/run` — запустить операции на текущей сессии

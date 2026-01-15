#!/bin/bash

if [ -z "$VIRTUAL_ENV" ]; then
    echo "ОШИБКА: venv не активирован!"
    echo "Запустите: source venv/bin/activate"
    exit 1
fi

echo "=== Starting CTnSS Local UI ==="
echo ""
echo "✓ venv активирован: $VIRTUAL_ENV"
echo ""
echo "API will be available at: http://127.0.0.1:8000"
echo "Web UI will be available at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

trap 'kill 0' EXIT

cd "$(dirname "$0")"

cd api
PYTHONPATH=../../src python -m uvicorn ctmsn_api.app:app --reload --host 127.0.0.1 --port 8000 &
API_PID=$!

cd ../web
npm run dev &
WEB_PID=$!

echo ""
echo "Servers started:"
echo "  API PID: $API_PID"
echo "  Web PID: $WEB_PID"
echo ""

wait

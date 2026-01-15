.PHONY: help install-api install-web install dev-api dev-web dev clean check-venv

help:
	@echo "CTnSS Local UI - Development Commands"
	@echo ""
	@echo "ВАЖНО: Активируйте venv перед использованием:"
	@echo "  source venv/bin/activate"
	@echo ""
	@echo "make install       - Установить все зависимости (API + Web)"
	@echo "make install-api   - Установить зависимости API"
	@echo "make install-web   - Установить зависимости Web"
	@echo ""
	@echo "make dev          - Запустить API и Web одновременно (в фоне)"
	@echo "make dev-api      - Запустить только API сервер"
	@echo "make dev-web      - Запустить только Web сервер"
	@echo ""
	@echo "make clean        - Остановить все dev-серверы"

check-venv:
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "ОШИБКА: venv не активирован!"; \
		echo "Запустите: source venv/bin/activate"; \
		exit 1; \
	fi
	@echo "✓ venv активирован: $$VIRTUAL_ENV"

install: install-api install-web

install-api: check-venv
	@echo "Installing API dependencies..."
	cd apps/api && python3 -m pip install -r requirements.txt

install-web:
	@echo "Installing Web dependencies..."
	cd apps/web && npm install

dev-api: check-venv
	@echo "Starting API server on http://127.0.0.1:8000"
	cd apps/api && PYTHONPATH=../../src:src python3 -m uvicorn ctmsn_api.app:app --reload --host 127.0.0.1 --port 8000

dev-web:
	@echo "Starting Web server on http://localhost:3000"
	cd apps/web && npm run dev

dev: check-venv
	@echo "Starting API and Web servers..."
	@echo "API: http://127.0.0.1:8000"
	@echo "Web: http://localhost:3000"
	@echo ""
	@echo "Press Ctrl+C to stop all servers"
	@make -j2 dev-api dev-web

clean:
	@echo "Stopping dev servers..."
	@pkill -f "uvicorn ctmsn_api.app:app" || true
	@pkill -f "next dev" || true
	@echo "Done"

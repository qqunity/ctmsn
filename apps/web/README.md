# CTMSN Web UI

Next.js frontend для локального UI.

## Установка

```bash
cd apps/web
npm install
```

## Запуск

```bash
cd apps/web
npm run dev
```

Клиент: `http://localhost:3000`

## API endpoint

По умолчанию frontend использует `http://127.0.0.1:8000`.

Для переопределения создайте `.env.local`:

```bash
NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000
```

## Основные экраны

- Авторизация: `/login`, `/register`
- Список рабочих пространств: `/workspaces`
- Рабочее пространство: `/workspace/[id]`
- Teacher: `/teacher`, `/teacher/student/[id]`

## Через Makefile (из корня репозитория)

```bash
make install-web
make dev-web
```

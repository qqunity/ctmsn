# CTnSS Web UI

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

UI будет доступен на `http://localhost:3000`

## Переменные окружения

По умолчанию используется `http://127.0.0.1:8000` для API.

Если нужно изменить, создайте файл `.env.local`:

```bash
echo "NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000" > .env.local
```

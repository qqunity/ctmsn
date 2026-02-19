# Быстрый старт по документации

Точка входа: [README.md](README.md)

## Короткие маршруты

### Ядро библиотеки
`README.md` → `USAGE.md` → `FORCING_IMPLEMENTATION.md`

### Сценарии
`USAGE.md` → `src/ctmsn/scenarios/README.md` → `src/ctmsn/scenarios/*/README.md`

### Локальный UI
`README.md` → `apps/api/README.md` + `apps/web/README.md` → `tests/e2e_*.py`

## Основные документы

- [README.md](README.md)
- [USAGE.md](USAGE.md)
- [FORCING_IMPLEMENTATION.md](FORCING_IMPLEMENTATION.md)
- [src/ctmsn/scenarios/README.md](src/ctmsn/scenarios/README.md)
- [NAVIGATION.md](NAVIGATION.md)
- [DOCUMENTATION_SUMMARY.md](DOCUMENTATION_SUMMARY.md)

## Команды для быстрой проверки

```bash
python3 src/ctmsn/examples/hello_forcing.py
python3 tests/test_smoke_imports.py
python3 tests/test_fast_smith.py
```

Для UI:

```bash
source venv/bin/activate
make install
make dev
```

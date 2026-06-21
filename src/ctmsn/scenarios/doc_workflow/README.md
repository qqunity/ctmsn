# Сценарий «Документооборот» (doc_workflow)

Витринный сценарий, объединяющий все доработки исследовательской платформы:
переходные/устойчивые режимы, инварианты, форсинг, формальную верификацию,
экспериментальные метрики и декларативный DSL. Используется в
[ЛР 6](../../../../docs/LAB6_WORKFLOW_INSTRUCTION.md).

## Предметная область

Документ проходит статусы `draft → review → approved → published`, находясь в
каждый момент ровно в одном статусе (денотационный инвариант согласованности).
Статус `rejected` — побочная ветвь (возврат на доработку по событию).

- Концепты: `doc`, статусы (`draft`, `review`, `approved`, `published`, `rejected`),
  рецензенты (`alice`, `bob`).
- Предикаты: `status(doc, stage)`, `assigned(doc, reviewer)`.
- Начальное состояние: `status(doc, draft)`, `assigned(doc, alice)`.

## Правила переходов

| Правило | Гвард | Эффект | Тип |
|---|---|---|---|
| `submit` | `status(doc, draft)` | draft → review | автономное |
| `approve` | `status(doc, review)` | review → approved | автономное |
| `publish` | `status(doc, approved)` | approved → published | автономное |
| `reject` | `status(doc, review)` | review → draft | событийное (`reject`), приоритет 1 |

Инвариант: `Or(status(doc, s))` по всем статусам. Устойчивый режим — `published`.

## Структура пакета

| Файл | Назначение |
|---|---|
| `model.py` | `build_network()` — сеть |
| `params.py` | `build_variables(net)` — переменная `reviewer` |
| `constraints.py` | `build_conditions(net)` — условия форсинга |
| `goal.py` | `build_goal(net)` — цель (опубликован + подобран рецензент) |
| `transition.py` | `build_rules(net)`, `build_invariants(net)` — переходы и инвариант |
| `model_doc.py` | `build_model()` — декларативная модель (DSL) для round-trip |
| `experiment.py` | `build_case()` — кейс для метрик |
| `runner.py` | `run()` — полный конвейер: форсинг → переходы → верификация → метрики → DSL |

## Запуск

```bash
python3 src/ctmsn/examples/doc_workflow_demo.py        # полный конвейер
python3 -m pytest tests/scenarios/test_doc_workflow.py # тесты сценария
```

Сценарий зарегистрирован в API (`doc_workflow`) и доступен в веб-интерфейсе для
построения правил переходов в панели «Переходы».

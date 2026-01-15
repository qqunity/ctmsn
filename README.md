# CTMSN - Composable Typed Modules for Semantic Networks

Система для работы с семантическими сетями, параметризацией и форсингом.

## Структура

- `core/` - ядро семантической сети (концепты, предикаты, факты)
- `param/` - параметризация (домены, переменные, контексты)
- `logic/` - логический слой (формулы, оценка)
- `forcing/` - форсинг-движок
- `io/` - сериализация
- `examples/` - примеры использования

## Установка

```bash
pip install -e .
```

## Быстрый старт

```python
from ctmsn.core.concept import Concept
from ctmsn.core.predicate import Predicate
from ctmsn.core.network import SemanticNetwork

net = SemanticNetwork()
alice = Concept("alice", "Alice")
net.add_concept(alice)
```

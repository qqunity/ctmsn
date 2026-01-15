from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Iterable, Iterator, Optional, Set, Tuple

from ctmsn.core.concept import Concept
from ctmsn.core.predicate import Predicate
from ctmsn.core.statement import Statement, CoreTerm


@dataclass
class SemanticNetwork:
    concepts: Dict[str, Concept] = field(default_factory=dict)
    predicates: Dict[str, Predicate] = field(default_factory=dict)

    _facts: Set[Statement] = field(default_factory=set)
    _facts_by_pred: Dict[str, Set[Statement]] = field(default_factory=dict)
    _facts_by_concept: Dict[str, Set[Statement]] = field(default_factory=dict)

    def add_concept(self, concept: Concept) -> None:
        if concept.id in self.concepts:
            raise ValueError(f"Concept '{concept.id}' already exists")
        self.concepts[concept.id] = concept

    def add_predicate(self, pred: Predicate) -> None:
        if pred.name in self.predicates:
            raise ValueError(f"Predicate '{pred.name}' already exists")
        self.predicates[pred.name] = pred

    def assert_fact(self, predicate: str, args: Tuple[CoreTerm, ...]) -> Statement:
        if predicate not in self.predicates:
            raise KeyError(f"Unknown predicate '{predicate}'")
        pred = self.predicates[predicate]
        if len(args) != pred.arity:
            raise ValueError(f"Arity mismatch: {predicate} expects {pred.arity}, got {len(args)}")

        st = Statement(predicate=predicate, args=args)
        if st in self._facts:
            return st

        self._facts.add(st)
        self._facts_by_pred.setdefault(predicate, set()).add(st)

        for a in args:
            if isinstance(a, Concept):
                self._facts_by_concept.setdefault(a.id, set()).add(st)

        return st

    def facts(self, predicate: str | None = None) -> Iterable[Statement]:
        if predicate is None:
            return set(self._facts)
        return set(self._facts_by_pred.get(predicate, set()))

    def validate(self) -> None:
        for st in self._facts:
            if st.predicate not in self.predicates:
                raise ValueError(f"Fact references unknown predicate '{st.predicate}'")
            if len(st.args) != self.predicates[st.predicate].arity:
                raise ValueError(f"Fact '{st}' has arity mismatch")

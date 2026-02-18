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

    def remove_concept(self, concept_id: str) -> Set[Statement]:
        if concept_id not in self.concepts:
            raise KeyError(f"Unknown concept '{concept_id}'")
        del self.concepts[concept_id]
        removed: Set[Statement] = set()
        refs = self._facts_by_concept.pop(concept_id, set())
        for st in refs:
            removed.add(st)
            self._facts.discard(st)
            bp = self._facts_by_pred.get(st.predicate)
            if bp:
                bp.discard(st)
            for a in st.args:
                if isinstance(a, Concept) and a.id != concept_id:
                    bc = self._facts_by_concept.get(a.id)
                    if bc:
                        bc.discard(st)
        return removed

    def remove_predicate(self, predicate_name: str) -> Set[Statement]:
        if predicate_name not in self.predicates:
            raise KeyError(f"Unknown predicate '{predicate_name}'")
        del self.predicates[predicate_name]
        removed = self._facts_by_pred.pop(predicate_name, set())
        for st in removed:
            self._facts.discard(st)
            for a in st.args:
                if isinstance(a, Concept):
                    bc = self._facts_by_concept.get(a.id)
                    if bc:
                        bc.discard(st)
        return removed

    def remove_fact(self, statement: Statement) -> None:
        if statement not in self._facts:
            raise KeyError(f"Fact not found: {statement}")
        self._facts.discard(statement)
        bp = self._facts_by_pred.get(statement.predicate)
        if bp:
            bp.discard(statement)
        for a in statement.args:
            if isinstance(a, Concept):
                bc = self._facts_by_concept.get(a.id)
                if bc:
                    bc.discard(statement)

    def replace_concept(self, old_id: str, new_concept: Concept) -> None:
        if old_id not in self.concepts:
            raise KeyError(f"Unknown concept '{old_id}'")
        if new_concept.id != old_id:
            raise ValueError("replace_concept requires same id; use remove+add for id change")
        self.concepts[old_id] = new_concept
        old_facts = list(self._facts_by_concept.get(old_id, set()))
        for st in old_facts:
            self._facts.discard(st)
            bp = self._facts_by_pred.get(st.predicate)
            if bp:
                bp.discard(st)
            for a in st.args:
                if isinstance(a, Concept):
                    bc = self._facts_by_concept.get(a.id)
                    if bc:
                        bc.discard(st)
            new_args = tuple(new_concept if (isinstance(a, Concept) and a.id == old_id) else a for a in st.args)
            new_st = Statement(predicate=st.predicate, args=new_args)
            self._facts.add(new_st)
            self._facts_by_pred.setdefault(st.predicate, set()).add(new_st)
            for a in new_args:
                if isinstance(a, Concept):
                    self._facts_by_concept.setdefault(a.id, set()).add(new_st)

    def replace_predicate(self, old_name: str, new_predicate: Predicate) -> None:
        if old_name not in self.predicates:
            raise KeyError(f"Unknown predicate '{old_name}'")
        if new_predicate.name != old_name:
            raise ValueError("replace_predicate requires same name")
        existing_facts = self._facts_by_pred.get(old_name, set())
        if existing_facts and new_predicate.arity != self.predicates[old_name].arity:
            raise ValueError(
                f"Cannot change arity of '{old_name}' from {self.predicates[old_name].arity} "
                f"to {new_predicate.arity}: {len(existing_facts)} facts exist"
            )
        self.predicates[old_name] = new_predicate

    def validate(self) -> None:
        for st in self._facts:
            if st.predicate not in self.predicates:
                raise ValueError(f"Fact references unknown predicate '{st.predicate}'")
            if len(st.args) != self.predicates[st.predicate].arity:
                raise ValueError(f"Fact '{st}' has arity mismatch")

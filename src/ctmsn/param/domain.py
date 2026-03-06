from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Callable, Iterable, Any


class Domain:
    def contains(self, value: Any) -> bool:
        raise NotImplementedError

    def describe(self) -> str:
        return self.__class__.__name__

    def enumerate_values(self) -> Iterable[Any]:
        raise TypeError(f"{self.__class__.__name__} is not enumerable")


@dataclass(frozen=True)
class EnumDomain(Domain):
    values: tuple[Any, ...]

    def contains(self, value: Any) -> bool:
        return value in self.values

    def describe(self) -> str:
        return f"Enum{self.values}"

    def enumerate_values(self) -> Iterable[Any]:
        return self.values


@dataclass(frozen=True)
class RangeDomain(Domain):
    min_value: float
    max_value: float
    inclusive: bool = True

    def contains(self, value: Any) -> bool:
        try:
            v = float(value)
        except Exception:
            return False
        if self.inclusive:
            return self.min_value <= v <= self.max_value
        return self.min_value < v < self.max_value

    def describe(self) -> str:
        b1 = "[" if self.inclusive else "("
        b2 = "]" if self.inclusive else ")"
        return f"Range{b1}{self.min_value}, {self.max_value}{b2}"

    def enumerate_values(self) -> Iterable[int]:
        if self.inclusive:
            lo = math.ceil(self.min_value)
            hi = math.floor(self.max_value)
        else:
            lo = math.floor(self.min_value) + 1
            hi = math.ceil(self.max_value) - 1
        return range(lo, hi + 1)


@dataclass(frozen=True)
class PredicateDomain(Domain):
    fn: Callable[[Any], bool]
    name: str = "PredicateDomain"

    def contains(self, value: Any) -> bool:
        return bool(self.fn(value))

    def describe(self) -> str:
        return self.name

from __future__ import annotations

from dataclasses import dataclass

from ctmsn.param.domain import EnumDomain
from ctmsn.param.variable import Variable
from ctmsn.param.context import Context
from ctmsn.core.network import SemanticNetwork


@dataclass(frozen=True)
class Lab5Vars:
    species: Variable
    individual: Variable


def build_variables(net: SemanticNetwork) -> tuple[Lab5Vars, Context]:
    penguin = net.concepts["penguin"]
    sparrow = net.concepts["sparrow"]
    salmon = net.concepts["salmon"]
    tux = net.concepts["tux"]
    jack = net.concepts["jack"]
    nemo = net.concepts["nemo"]

    v = Lab5Vars(
        species=Variable("species", EnumDomain((penguin, sparrow, salmon))),
        individual=Variable("individual", EnumDomain((tux, jack, nemo))),
    )

    ctx0 = Context()

    return v, ctx0

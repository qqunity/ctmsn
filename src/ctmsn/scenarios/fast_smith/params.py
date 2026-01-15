from __future__ import annotations

from dataclasses import dataclass

from ctmsn.param.domain import EnumDomain
from ctmsn.param.variable import Variable
from ctmsn.param.context import Context
from ctmsn.core.network import SemanticNetwork


@dataclass(frozen=True)
class FastSmithVars:
    x: Variable
    y: Variable
    label: Variable

    person: Variable
    spouse: Variable
    name: Variable


def build_variables(net: SemanticNetwork) -> tuple[FastSmithVars, Context]:
    nodes = (
        net.concepts["A"],
        net.concepts["B"],
        net.concepts["T"],
        net.concepts["T_minus"],
        net.concepts["T_plus"],
        net.concepts["Cf_minus"],
        net.concepts["Cf_plus"],
    )

    labels = ("f", "s", "sf", "h", "g", "not-g", "r", "j", "jf", "r∘sf", "incl")

    people = (net.concepts["A"], net.concepts["J"])
    spouses = (net.concepts["S"], net.concepts["C"])
    names = (net.concepts["J"],)

    v = FastSmithVars(
        x=Variable("x", EnumDomain(nodes)),
        y=Variable("y", EnumDomain(nodes)),
        label=Variable("label", EnumDomain(labels)),
        person=Variable("person", EnumDomain(people)),
        spouse=Variable("spouse", EnumDomain(spouses)),
        name=Variable("name", EnumDomain(names)),
    )

    ctx0 = Context()
    ctx0.set(v.x, net.concepts["A"])
    ctx0.set(v.label, "h")

    return v, ctx0

from ctmsn.core.concept import Concept
from ctmsn.core.predicate import Predicate
from ctmsn.core.network import SemanticNetwork

from ctmsn.param.domain import EnumDomain
from ctmsn.param.variable import Variable
from ctmsn.param.context import Context

from ctmsn.logic.formula import FactAtom, And, Not
from ctmsn.forcing.conditions import Conditions
from ctmsn.forcing.engine import ForcingEngine


def build_network() -> SemanticNetwork:
    net = SemanticNetwork()

    alice = Concept("alice", "Alice")
    bob = Concept("bob", "Bob")
    carol = Concept("carol", "Carol")

    for c in (alice, bob, carol):
        net.add_concept(c)

    net.add_predicate(Predicate(name="knows", arity=2, roles=("who", "whom")))
    net.add_predicate(Predicate(name="blocked", arity=2, roles=("who", "whom")))

    net.assert_fact("knows", (alice, bob))
    net.assert_fact("knows", (bob, carol))
    net.assert_fact("blocked", (alice, carol))

    net.validate()
    return net


def case_already_forced(net: SemanticNetwork) -> None:
    print("\n=== CASE 1: phi already TRUE in given context ===")

    domain_people = EnumDomain(tuple(net.concepts.values()))
    x = Variable("x", domain_people)
    y = Variable("y", domain_people)

    ctx = Context()
    ctx.set(x, net.concepts["alice"])
    ctx.set(y, net.concepts["bob"])

    phi = FactAtom("knows", (x, y))

    conds = Conditions()

    eng = ForcingEngine(net)
    print("forces(ctx, phi) =", eng.forces(ctx, phi, conds).value)
    res = eng.force(ctx, phi, conds)
    print("force(ctx, phi)  =", res.status.value, "|", res.explanation)


def case_unknown_without_search(net: SemanticNetwork) -> None:
    print("\n=== CASE 2: phi UNKNOWN because context incomplete ===")

    domain_people = EnumDomain(tuple(net.concepts.values()))
    x = Variable("x", domain_people)
    y = Variable("y", domain_people)

    ctx = Context()
    ctx.set(x, net.concepts["bob"])

    phi = FactAtom("knows", (x, y))

    conds = Conditions().add(Not(FactAtom("blocked", (x, y))))

    eng = ForcingEngine(net)
    print("forces(ctx, phi) =", eng.forces(ctx, phi, conds).value)

    res = eng.force(ctx, phi, conds)
    print("force(ctx, phi)  =", res.status.value, "|", res.explanation)


def case_forced_by_full_assignment(net: SemanticNetwork) -> None:
    print("\n=== CASE 3: show constraints with full assignment ===")

    domain_people = EnumDomain(tuple(net.concepts.values()))
    x = Variable("x", domain_people)
    y = Variable("y", domain_people)

    ctx = Context()
    ctx.set(x, net.concepts["alice"])
    ctx.set(y, net.concepts["carol"])

    conds = Conditions().add(
        Not(FactAtom("blocked", (x, y))),
    )

    phi = FactAtom("knows", (x, y))

    eng = ForcingEngine(net)
    chk = eng.check(ctx, conds)
    print("check ok =", chk.ok, "| violated =", chk.violated, "| unknown =", chk.unknown)
    print("forces(ctx, phi) =", eng.forces(ctx, phi, conds).value)
    res = eng.force(ctx, phi, conds)
    print("force(ctx, phi)  =", res.status.value, "|", res.explanation)
    print("NOTE: Here conditions are violated because blocked(alice, carol) is TRUE in the network.")


def main():
    net = build_network()
    case_already_forced(net)
    case_unknown_without_search(net)
    case_forced_by_full_assignment(net)


if __name__ == "__main__":
    main()

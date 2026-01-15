from ctmsn.core.concept import Concept
from ctmsn.core.predicate import Predicate
from ctmsn.core.network import SemanticNetwork

from ctmsn.param.domain import EnumDomain
from ctmsn.param.variable import Variable
from ctmsn.param.context import Context

from ctmsn.logic.formula import FactAtom
from ctmsn.forcing.conditions import Conditions
from ctmsn.forcing.engine import ForcingEngine


def main():
    net = SemanticNetwork()

    alice = Concept("alice", "Alice")
    bob = Concept("bob", "Bob")
    net.add_concept(alice)
    net.add_concept(bob)

    net.add_predicate(Predicate(name="knows", arity=2, roles=("who", "whom")))

    net.assert_fact("knows", (alice, bob))

    x = Variable("x", domain=EnumDomain((alice, bob)))
    y = Variable("y", domain=EnumDomain((alice, bob)))

    ctx = Context()
    ctx.set(x, alice)
    ctx.set(y, bob)

    phi = FactAtom("knows", (x, y))

    eng = ForcingEngine(net=net)
    res = eng.force(ctx, phi, Conditions())
    print("forces:", eng.forces(ctx, phi, Conditions()).value)
    print("force result:", res.status.value, res.explanation)


if __name__ == "__main__":
    main()

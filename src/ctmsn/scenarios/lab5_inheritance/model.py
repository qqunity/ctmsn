from __future__ import annotations

from ctmsn.core.concept import Concept
from ctmsn.core.predicate import Predicate
from ctmsn.core.network import SemanticNetwork


def build_network() -> SemanticNetwork:
    """
    Предметная область «Зоологическая классификация».
    12 концептов, 5 бинарных предикатов, 15 фактов.
    Демонстрация наследования, исключений и рассуждений
    при неполной информации.
    """

    net = SemanticNetwork()

    # --- Concepts ---
    animal = Concept("animal", "Животное")
    bird = Concept("bird", "Птица")
    fish = Concept("fish", "Рыба")
    penguin = Concept("penguin", "Пингвин")
    sparrow = Concept("sparrow", "Воробей")
    salmon = Concept("salmon", "Лосось")
    tux = Concept("tux", "Tux")
    jack = Concept("jack", "Jack")
    nemo = Concept("nemo", "Nemo")
    ability_fly = Concept("ability_fly", "Способность летать")
    ability_swim = Concept("ability_swim", "Способность плавать")
    ability_breathe = Concept("ability_breathe", "Способность дышать")

    for c in (
        animal, bird, fish, penguin, sparrow, salmon,
        tux, jack, nemo, ability_fly, ability_swim, ability_breathe,
    ):
        net.add_concept(c)

    # --- Predicates ---
    net.add_predicate(Predicate("isa", 2, roles=("child", "parent")))
    net.add_predicate(Predicate("instance_of", 2, roles=("individual", "class")))
    net.add_predicate(Predicate("has_ability", 2, roles=("entity", "ability")))
    net.add_predicate(Predicate("lacks_ability", 2, roles=("entity", "ability")))
    net.add_predicate(Predicate("knows_about", 2, roles=("subject", "object")))

    # --- ISA hierarchy ---
    net.assert_fact("isa", (bird, animal))
    net.assert_fact("isa", (fish, animal))
    net.assert_fact("isa", (penguin, bird))
    net.assert_fact("isa", (sparrow, bird))
    net.assert_fact("isa", (salmon, fish))

    # --- Instances ---
    net.assert_fact("instance_of", (tux, penguin))
    net.assert_fact("instance_of", (jack, sparrow))
    net.assert_fact("instance_of", (nemo, salmon))

    # --- Abilities ---
    net.assert_fact("has_ability", (animal, ability_breathe))
    net.assert_fact("has_ability", (bird, ability_fly))
    net.assert_fact("has_ability", (fish, ability_swim))
    net.assert_fact("has_ability", (penguin, ability_swim))

    # --- Exception ---
    net.assert_fact("lacks_ability", (penguin, ability_fly))

    # --- Propositional ---
    net.assert_fact("knows_about", (jack, tux))
    net.assert_fact("knows_about", (nemo, jack))

    net.validate()
    return net

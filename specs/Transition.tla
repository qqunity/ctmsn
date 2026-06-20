---------------------------- MODULE Transition ----------------------------
(***************************************************************************)
(* Формальная спецификация переходной системы CTMSN (ступенчатый процесс).*)
(* Соответствие коду см. в docs/VERIFICATION.md:                          *)
(*   at            <-> факты at(obj, s_i) в SemanticNetwork                *)
(*   Init          <-> начальное состояние make_state (объект на s0)       *)
(*   Advance(i)    <-> TransitionRule s_i->s_{i+1} (retract+add)           *)
(*   Consistency   <-> денотационный инвариант (Conditions/ForcingEngine)  *)
(*   Termination   <-> сходимость к устойчивому режиму (StateMode.STABLE)  *)
(***************************************************************************)
EXTENDS Naturals, FiniteSets

CONSTANT N        \* число стадий (>= 2)
CONSTANT Faulty   \* BOOLEAN: переход s0->s1 «теряет» объект (дефект)

VARIABLE at       \* множество занятых стадий, подмножество 0..N-1

Stages == 0 .. (N - 1)

TypeOK == at \subseteq Stages

Init == at = {0}

(* Переход: объект на стадии i переходит на i+1 (снять i, добавить i+1).   *)
(* При Faulty и i = 0 объект теряется (add не выполняется) — дефект.        *)
Advance(i) ==
    /\ i \in at
    /\ i < N - 1
    /\ at' = (at \ {i}) \cup (IF Faulty /\ i = 0 THEN {} ELSE {i + 1})

Next == \E i \in Stages : Advance(i)

Spec == Init /\ [][Next]_at /\ WF_at(Next)

(* Безопасность: объект всегда ровно на одной стадии (согласованность).    *)
Consistency == Cardinality(at) = 1

(* Живость: объект в итоге достигает финальной стадии (сходимость).        *)
Termination == <>(at = {N - 1})
===========================================================================

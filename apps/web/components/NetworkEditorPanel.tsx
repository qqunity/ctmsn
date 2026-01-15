"use client";

import { useState } from "react";
import { addConcept, addPredicate, addFact } from "@/lib/api";
import { GraphPayload } from "@/lib/types";

type EditorMode = "concept" | "predicate" | "fact";

export function NetworkEditorPanel({
  sessionId,
  graph,
  onUpdate,
}: {
  sessionId: string;
  graph: GraphPayload | null;
  onUpdate: (graph: GraphPayload) => void;
}) {
  const [mode, setMode] = useState<EditorMode>("concept");
  const [error, setError] = useState<string>("");

  const [conceptId, setConceptId] = useState("");
  const [conceptLabel, setConceptLabel] = useState("");
  const [conceptTags, setConceptTags] = useState("");

  const [predicateName, setPredicateName] = useState("");
  const [predicateArity, setPredicateArity] = useState("2");

  const [factPredicate, setFactPredicate] = useState("");
  const [factArgs, setFactArgs] = useState<string[]>([]);
  const [factArgsManual, setFactArgsManual] = useState("");

  async function handleAddConcept() {
    if (!sessionId || !conceptId || !conceptLabel) {
      setError("Session, ID и Label обязательны");
      return;
    }

    const result = await addConcept({
      session_id: sessionId,
      id: conceptId,
      label: conceptLabel,
      tags: conceptTags ? conceptTags.split(",").map((t) => t.trim()) : [],
    });

    if (result.error) {
      setError(result.error);
    } else if (result.graph) {
      setError("");
      setConceptId("");
      setConceptLabel("");
      setConceptTags("");
      onUpdate(result.graph);
    }
  }

  async function handleAddPredicate() {
    if (!sessionId || !predicateName) {
      setError("Session и Name обязательны");
      return;
    }

    const result = await addPredicate({
      session_id: sessionId,
      name: predicateName,
      arity: parseInt(predicateArity),
    });

    if (result.error) {
      setError(result.error);
    } else if (result.graph) {
      setError("");
      setPredicateName("");
      setPredicateArity("2");
      onUpdate(result.graph);
    }
  }

  async function handleAddFact() {
    if (!sessionId || !factPredicate || factArgs.length === 0) {
      setError("Session, Predicate и Args обязательны");
      return;
    }

    const result = await addFact({
      session_id: sessionId,
      predicate: factPredicate,
      args: factArgs,
    });

    if (result.error) {
      setError(result.error);
    } else if (result.graph) {
      setError("");
      setFactPredicate("");
      setFactArgs([]);
      setFactArgsManual("");
      onUpdate(result.graph);
    }
  }

  const concepts = graph?.nodes.map((n) => n.id) ?? [];
  const predicates = graph?.predicates ?? [];
  const selectedPredicate = predicates.find((p) => p.name === factPredicate);

  return (
    <div className="space-y-3">
      <div className="text-sm font-semibold">Network Editor</div>

      <div className="flex gap-2">
        <button
          className={`rounded px-2 py-1 text-xs ${
            mode === "concept"
              ? "bg-blue-500 text-white"
              : "bg-zinc-100 hover:bg-zinc-200"
          }`}
          onClick={() => setMode("concept")}
        >
          Concept
        </button>
        <button
          className={`rounded px-2 py-1 text-xs ${
            mode === "predicate"
              ? "bg-blue-500 text-white"
              : "bg-zinc-100 hover:bg-zinc-200"
          }`}
          onClick={() => setMode("predicate")}
        >
          Predicate
        </button>
        <button
          className={`rounded px-2 py-1 text-xs ${
            mode === "fact"
              ? "bg-blue-500 text-white"
              : "bg-zinc-100 hover:bg-zinc-200"
          }`}
          onClick={() => setMode("fact")}
        >
          Fact
        </button>
      </div>

      {error && (
        <div className="rounded bg-red-50 p-2 text-xs text-red-600">
          {error}
        </div>
      )}

      {mode === "concept" && (
        <div className="space-y-2 rounded-lg border bg-white p-3">
          <input
            className="w-full rounded border px-2 py-1 text-sm"
            placeholder="ID (например: concept1)"
            value={conceptId}
            onChange={(e) => setConceptId(e.target.value)}
          />
          <input
            className="w-full rounded border px-2 py-1 text-sm"
            placeholder="Label (например: Концепт 1)"
            value={conceptLabel}
            onChange={(e) => setConceptLabel(e.target.value)}
          />
          <input
            className="w-full rounded border px-2 py-1 text-sm"
            placeholder="Tags (через запятую)"
            value={conceptTags}
            onChange={(e) => setConceptTags(e.target.value)}
          />
          <button
            className="w-full rounded bg-blue-500 px-3 py-1 text-sm text-white hover:bg-blue-600"
            onClick={handleAddConcept}
          >
            Добавить концепт
          </button>
        </div>
      )}

      {mode === "predicate" && (
        <div className="space-y-2 rounded-lg border bg-white p-3">
          <input
            className="w-full rounded border px-2 py-1 text-sm"
            placeholder="Name (например: relates)"
            value={predicateName}
            onChange={(e) => setPredicateName(e.target.value)}
          />
          <input
            type="number"
            className="w-full rounded border px-2 py-1 text-sm"
            placeholder="Arity"
            value={predicateArity}
            onChange={(e) => setPredicateArity(e.target.value)}
          />
          <button
            className="w-full rounded bg-blue-500 px-3 py-1 text-sm text-white hover:bg-blue-600"
            onClick={handleAddPredicate}
          >
            Добавить предикат
          </button>
        </div>
      )}

      {mode === "fact" && (
        <div className="space-y-2 rounded-lg border bg-white p-3">
          <div className="text-xs text-zinc-600">Выберите предикат:</div>
          <select
            className="w-full rounded border px-2 py-1 text-sm"
            value={factPredicate}
            onChange={(e) => {
              setFactPredicate(e.target.value);
              setFactArgs([]);
            }}
          >
            <option value="">-- выберите --</option>
            {predicates.map((p) => (
              <option key={p.name} value={p.name}>
                {p.name} (арность: {p.arity})
              </option>
            ))}
          </select>

          {selectedPredicate && (
            <>
              <div className="text-xs text-zinc-600">
                Требуется аргументов: {selectedPredicate.arity}
              </div>
              
              <div className="text-xs text-zinc-600">
                Способ 1: Выберите концепты (в порядке следования):
              </div>
              <div className="max-h-32 space-y-1 overflow-auto rounded border bg-zinc-50 p-2">
                {concepts.map((c) => (
                  <button
                    key={c}
                    className={`w-full rounded px-2 py-1 text-left text-xs hover:bg-zinc-200 ${
                      factArgs.includes(c) ? "bg-blue-100" : ""
                    }`}
                    onClick={() => {
                      if (factArgs.length < selectedPredicate.arity && !factArgs.includes(c)) {
                        setFactArgs([...factArgs, c]);
                      }
                    }}
                  >
                    {c} {factArgs.includes(c) ? `(позиция ${factArgs.indexOf(c) + 1})` : ""}
                  </button>
                ))}
              </div>
              
              <div className="text-xs text-zinc-500">
                Выбрано ({factArgs.length}/{selectedPredicate.arity}): [{factArgs.join(", ")}]
              </div>

              {factArgs.length > 0 && (
                <button
                  className="w-full rounded bg-zinc-200 px-2 py-1 text-xs hover:bg-zinc-300"
                  onClick={() => setFactArgs([])}
                >
                  Очистить выбор
                </button>
              )}

              <div className="border-t pt-2">
                <div className="text-xs text-zinc-600">
                  Способ 2: Введите ID концептов через запятую:
                </div>
                <input
                  className="w-full rounded border px-2 py-1 text-sm"
                  placeholder="concept1, concept2, ..."
                  value={factArgsManual}
                  onChange={(e) => {
                    setFactArgsManual(e.target.value);
                    const ids = e.target.value.split(",").map((s) => s.trim()).filter((s) => s);
                    setFactArgs(ids);
                  }}
                />
              </div>

              <button
                className={`w-full rounded px-3 py-1 text-sm text-white ${
                  factArgs.length === selectedPredicate.arity
                    ? "bg-blue-500 hover:bg-blue-600"
                    : "bg-zinc-300 cursor-not-allowed"
                }`}
                onClick={handleAddFact}
                disabled={factArgs.length !== selectedPredicate.arity}
              >
                Добавить факт ({factArgs.length}/{selectedPredicate.arity})
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
}

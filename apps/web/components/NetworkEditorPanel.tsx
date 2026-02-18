"use client";

import { useState } from "react";
import {
  addConcept,
  addPredicate,
  addFact,
  removeConcept,
  removePredicate,
  removeFact,
  editConcept,
  editPredicate,
  getCascadeInfo,
} from "@/lib/api";
import { GraphPayload, CascadeInfo } from "@/lib/types";

type EditorMode = "concept" | "predicate" | "fact";

type EditingItem =
  | { type: "concept"; id: string; label: string; tags: string }
  | { type: "predicate"; name: string; arity: string }
  | null;

type CascadeWarning = {
  type: "concept" | "predicate";
  id: string;
  info: CascadeInfo;
} | null;

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

  const [editingItem, setEditingItem] = useState<EditingItem>(null);
  const [cascadeWarning, setCascadeWarning] = useState<CascadeWarning>(null);

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

  async function handleDeleteConcept(id: string) {
    const info = await getCascadeInfo(sessionId, "concept", id);
    if (info.count > 0) {
      setCascadeWarning({ type: "concept", id, info });
    } else {
      await confirmDeleteConcept(id);
    }
  }

  async function confirmDeleteConcept(id: string) {
    setCascadeWarning(null);
    const result = await removeConcept(sessionId, id);
    if (result.error) {
      setError(result.error);
    } else if (result.graph) {
      setError("");
      onUpdate(result.graph);
    }
  }

  async function handleDeletePredicate(name: string) {
    const info = await getCascadeInfo(sessionId, "predicate", name);
    if (info.count > 0) {
      setCascadeWarning({ type: "predicate", id: name, info });
    } else {
      await confirmDeletePredicate(name);
    }
  }

  async function confirmDeletePredicate(name: string) {
    setCascadeWarning(null);
    const result = await removePredicate(sessionId, name);
    if (result.error) {
      setError(result.error);
    } else if (result.graph) {
      setError("");
      onUpdate(result.graph);
    }
  }

  async function handleDeleteFact(predicate: string, args: string[]) {
    const result = await removeFact(sessionId, predicate, args);
    if (result.error) {
      setError(result.error);
    } else if (result.graph) {
      setError("");
      onUpdate(result.graph);
    }
  }

  async function handleSaveEdit() {
    if (!editingItem) return;
    if (editingItem.type === "concept") {
      const result = await editConcept(sessionId, editingItem.id, {
        label: editingItem.label,
        tags: editingItem.tags ? editingItem.tags.split(",").map((t) => t.trim()) : [],
      });
      if (result.error) {
        setError(result.error);
      } else if (result.graph) {
        setError("");
        onUpdate(result.graph);
      }
    } else {
      const result = await editPredicate(sessionId, editingItem.name, {
        arity: parseInt(editingItem.arity),
      });
      if (result.error) {
        setError(result.error);
      } else if (result.graph) {
        setError("");
        onUpdate(result.graph);
      }
    }
    setEditingItem(null);
  }

  const concepts = graph?.nodes ?? [];
  const predicates = graph?.predicates ?? [];
  const edges = graph?.edges ?? [];
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

      {cascadeWarning && (
        <div className="rounded border border-yellow-300 bg-yellow-50 p-3 text-xs space-y-2">
          <div className="font-semibold text-yellow-800">
            Удаление {cascadeWarning.type === "concept" ? "концепта" : "предиката"} &quot;{cascadeWarning.id}&quot; затронет {cascadeWarning.info.count} факт(ов):
          </div>
          <ul className="list-disc pl-4 text-yellow-700">
            {cascadeWarning.info.affected_facts.map((f, i) => (
              <li key={i}>{f.predicate}({f.args.join(", ")})</li>
            ))}
          </ul>
          <div className="flex gap-2">
            <button
              className="rounded bg-red-500 px-2 py-1 text-white hover:bg-red-600"
              onClick={() =>
                cascadeWarning.type === "concept"
                  ? confirmDeleteConcept(cascadeWarning.id)
                  : confirmDeletePredicate(cascadeWarning.id)
              }
            >
              Удалить
            </button>
            <button
              className="rounded bg-gray-200 px-2 py-1 hover:bg-gray-300"
              onClick={() => setCascadeWarning(null)}
            >
              Отмена
            </button>
          </div>
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

          {concepts.length > 0 && (
            <div className="border-t pt-2 mt-2">
              <div className="text-xs text-zinc-500 mb-1">Существующие концепты:</div>
              <div className="max-h-40 overflow-auto space-y-1">
                {concepts.map((c) => (
                  <div key={c.id} className="flex items-center gap-1 text-xs bg-zinc-50 rounded px-2 py-1">
                    {editingItem?.type === "concept" && editingItem.id === c.id ? (
                      <div className="flex-1 space-y-1">
                        <input
                          className="w-full rounded border px-1 py-0.5 text-xs"
                          value={editingItem.label}
                          onChange={(e) => setEditingItem({ ...editingItem, label: e.target.value })}
                          placeholder="Label"
                        />
                        <input
                          className="w-full rounded border px-1 py-0.5 text-xs"
                          value={editingItem.tags}
                          onChange={(e) => setEditingItem({ ...editingItem, tags: e.target.value })}
                          placeholder="Tags"
                        />
                        <div className="flex gap-1">
                          <button onClick={handleSaveEdit} className="text-green-600 hover:underline">OK</button>
                          <button onClick={() => setEditingItem(null)} className="text-gray-500 hover:underline">Отмена</button>
                        </div>
                      </div>
                    ) : (
                      <>
                        <span className="flex-1 truncate">
                          {c.id} ({c.label}){c.tags && c.tags.length > 0 ? ` [${c.tags.join(", ")}]` : ""}
                        </span>
                        <button
                          className="text-blue-500 hover:underline shrink-0"
                          onClick={() => setEditingItem({ type: "concept", id: c.id, label: c.label, tags: (c.tags ?? []).join(", ") })}
                        >
                          &#9998;
                        </button>
                        <button
                          className="text-red-500 hover:underline shrink-0"
                          onClick={() => handleDeleteConcept(c.id)}
                        >
                          &times;
                        </button>
                      </>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
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

          {predicates.length > 0 && (
            <div className="border-t pt-2 mt-2">
              <div className="text-xs text-zinc-500 mb-1">Существующие предикаты:</div>
              <div className="max-h-40 overflow-auto space-y-1">
                {predicates.map((p) => (
                  <div key={p.name} className="flex items-center gap-1 text-xs bg-zinc-50 rounded px-2 py-1">
                    {editingItem?.type === "predicate" && editingItem.name === p.name ? (
                      <div className="flex-1 space-y-1">
                        <input
                          type="number"
                          className="w-full rounded border px-1 py-0.5 text-xs"
                          value={editingItem.arity}
                          onChange={(e) => setEditingItem({ ...editingItem, arity: e.target.value })}
                          placeholder="Arity"
                        />
                        <div className="flex gap-1">
                          <button onClick={handleSaveEdit} className="text-green-600 hover:underline">OK</button>
                          <button onClick={() => setEditingItem(null)} className="text-gray-500 hover:underline">Отмена</button>
                        </div>
                      </div>
                    ) : (
                      <>
                        <span className="flex-1 truncate">{p.name} (арность: {p.arity})</span>
                        <button
                          className="text-blue-500 hover:underline shrink-0"
                          onClick={() => setEditingItem({ type: "predicate", name: p.name, arity: String(p.arity) })}
                        >
                          &#9998;
                        </button>
                        <button
                          className="text-red-500 hover:underline shrink-0"
                          onClick={() => handleDeletePredicate(p.name)}
                        >
                          &times;
                        </button>
                      </>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
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
                    key={c.id}
                    className={`w-full rounded px-2 py-1 text-left text-xs hover:bg-zinc-200 ${
                      factArgs.includes(c.id) ? "bg-blue-100" : ""
                    }`}
                    onClick={() => {
                      if (factArgs.length < selectedPredicate.arity && !factArgs.includes(c.id)) {
                        setFactArgs([...factArgs, c.id]);
                      }
                    }}
                  >
                    {c.id} {factArgs.includes(c.id) ? `(позиция ${factArgs.indexOf(c.id) + 1})` : ""}
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

          {edges.length > 0 && (
            <div className="border-t pt-2 mt-2">
              <div className="text-xs text-zinc-500 mb-1">Существующие факты:</div>
              <div className="max-h-40 overflow-auto space-y-1">
                {edges.filter((e) => e.kind === "edge").map((e) => (
                  <div key={e.id} className="flex items-center gap-1 text-xs bg-zinc-50 rounded px-2 py-1">
                    <span className="flex-1 truncate">{e.label}({e.source}, {e.target})</span>
                    <button
                      className="text-red-500 hover:underline shrink-0"
                      onClick={() => handleDeleteFact(e.label, [e.source, e.target])}
                    >
                      &times;
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

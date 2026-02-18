"use client";

import { useState, useEffect, useCallback } from "react";
import { listFormulas, createFormula, updateFormula, deleteFormula, evaluateFormula } from "@/lib/api";
import { FormulaInfo, FormulaNode, GraphPayload, VariableInfo } from "@/lib/types";
import { FormulaBuilder, formulaToText } from "./FormulaBuilder";

type Props = {
  sessionId: string;
  graph: GraphPayload | null;
  variables: VariableInfo[];
  activeTermPickerId: string | null;
  onTermPickerFocus: (id: string | null) => void;
};

const RESULT_COLORS: Record<string, string> = {
  true: "bg-green-100 text-green-700",
  false: "bg-red-100 text-red-700",
  unknown: "bg-yellow-100 text-yellow-700",
};

export function FormulaEditorPanel({ sessionId, graph, variables, activeTermPickerId, onTermPickerFocus }: Props) {
  const [formulas, setFormulas] = useState<FormulaInfo[]>([]);
  const [evalResults, setEvalResults] = useState<Record<string, string>>({});
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editFormula, setEditFormula] = useState<FormulaNode | null>(null);
  const [editName, setEditName] = useState("");
  const [showNew, setShowNew] = useState(false);
  const [newName, setNewName] = useState("");
  const [newFormula, setNewFormula] = useState<FormulaNode>({ type: "FactAtom", predicate: "", args: [] });

  const fetchFormulas = useCallback(async () => {
    try {
      const list = await listFormulas(sessionId);
      setFormulas(list);
    } catch {
      // ignore
    }
  }, [sessionId]);

  useEffect(() => {
    fetchFormulas();
  }, [fetchFormulas]);

  async function handleCreate() {
    if (!newName.trim()) return;
    try {
      await createFormula(sessionId, newName.trim(), newFormula);
      setShowNew(false);
      setNewName("");
      setNewFormula({ type: "FactAtom", predicate: "", args: [] });
      await fetchFormulas();
    } catch (e: any) {
      alert(e.message || "Error creating formula");
    }
  }

  async function handleSaveEdit() {
    if (!editingId) return;
    try {
      await updateFormula(sessionId, editingId, {
        name: editName || undefined,
        formula: editFormula ?? undefined,
      });
      setEditingId(null);
      setEditFormula(null);
      await fetchFormulas();
    } catch (e: any) {
      alert(e.message || "Error updating formula");
    }
  }

  async function handleDelete(fid: string) {
    try {
      await deleteFormula(sessionId, fid);
      await fetchFormulas();
    } catch (e: any) {
      alert(e.message || "Error deleting formula");
    }
  }

  async function handleEvaluate(fid: string) {
    try {
      const res = await evaluateFormula(sessionId, fid);
      setEvalResults((prev) => ({ ...prev, [fid]: res.result }));
    } catch (e: any) {
      alert(e.message || "Error evaluating formula");
    }
  }

  return (
    <div>
      <h3 className="text-sm font-semibold mb-2">Формулы</h3>

      {formulas.length === 0 && !showNew && (
        <p className="text-xs text-gray-400 mb-2">Нет формул</p>
      )}

      <div className="space-y-2 mb-2">
        {formulas.map((f) => {
          const isEditing = editingId === f.id;
          const evalResult = evalResults[f.id];

          return (
            <div key={f.id} className="border rounded text-xs">
              <div className="flex items-center gap-1 px-2 py-1">
                <button
                  onClick={() => {
                    if (isEditing) {
                      setEditingId(null);
                      setEditFormula(null);
                    } else {
                      setEditingId(f.id);
                      setEditName(f.name);
                      setEditFormula(f.formula);
                    }
                  }}
                  className="flex-1 text-left hover:text-blue-600 truncate font-medium"
                >
                  {f.name}
                </button>
                {evalResult && (
                  <span className={`px-1.5 py-0.5 rounded text-[10px] ${RESULT_COLORS[evalResult] ?? "bg-gray-100"}`}>
                    {evalResult}
                  </span>
                )}
                <button onClick={() => handleEvaluate(f.id)} className="text-blue-500 hover:text-blue-700" title="Вычислить">
                  &#9654;
                </button>
                <button onClick={() => handleDelete(f.id)} className="text-red-400 hover:text-red-600" title="Удалить">
                  &times;
                </button>
              </div>
              {!isEditing && (
                <div className="px-2 pb-1 text-[10px] text-gray-400 font-mono truncate">{f.text}</div>
              )}
              {isEditing && editFormula && (
                <div className="border-t p-2 bg-gray-50 space-y-2">
                  <input
                    type="text"
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    className="border rounded px-2 py-1 text-xs w-full"
                  />
                  <FormulaBuilder
                    value={editFormula}
                    onChange={setEditFormula}
                    graph={graph}
                    variables={variables}
                    activeTermPickerId={activeTermPickerId}
                    onTermPickerFocus={onTermPickerFocus}
                    path={`edit-${f.id}`}
                  />
                  <div className="flex gap-2 justify-end">
                    <button onClick={() => { setEditingId(null); setEditFormula(null); }} className="text-xs text-gray-500 hover:underline">Отмена</button>
                    <button onClick={handleSaveEdit} className="text-xs bg-green-600 text-white px-3 py-1 rounded">Сохранить</button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {showNew ? (
        <div className="border rounded p-2 bg-gray-50 space-y-2">
          <input
            type="text"
            placeholder="Имя формулы"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            className="border rounded px-2 py-1 text-xs w-full"
            autoFocus
          />
          <FormulaBuilder
            value={newFormula}
            onChange={setNewFormula}
            graph={graph}
            variables={variables}
            activeTermPickerId={activeTermPickerId}
            onTermPickerFocus={onTermPickerFocus}
            path="new"
          />
          <div className="flex gap-2 justify-end">
            <button onClick={() => { setShowNew(false); setNewName(""); }} className="text-xs text-gray-500 hover:underline">Отмена</button>
            <button onClick={handleCreate} disabled={!newName.trim()} className="text-xs bg-green-600 text-white px-3 py-1 rounded disabled:opacity-50">Создать</button>
          </div>
        </div>
      ) : (
        <button onClick={() => setShowNew(true)} className="text-xs text-blue-600 hover:underline">
          + Новая формула
        </button>
      )}
    </div>
  );
}

"use client";

import { useState, useEffect, useCallback } from "react";
import {
  listContexts,
  createContext,
  deleteContext,
  activateContext,
  setContextVariable,
  compareContexts,
  getContextHighlights,
} from "@/lib/api";
import { NamedContextInfo, ContextCompareResult, VariableInfo, ContextHighlights } from "@/lib/types";
import { ContextCompareView } from "./ContextCompareView";

type Props = {
  sessionId: string;
  variables: VariableInfo[];
  onActivate?: () => void;
  onHighlightsChange?: (h: ContextHighlights) => void;
};

export function ContextEditorPanel({ sessionId, variables, onActivate, onHighlightsChange }: Props) {
  const [contexts, setContexts] = useState<NamedContextInfo[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [cloneFrom, setCloneFrom] = useState("");
  const [compareResult, setCompareResult] = useState<ContextCompareResult | null>(null);
  const [compareIds, setCompareIds] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(false);

  const fetchContexts = useCallback(async () => {
    try {
      const list = await listContexts(sessionId);
      setContexts(list);
    } catch {
      // ignore
    }
  }, [sessionId]);

  useEffect(() => {
    fetchContexts();
  }, [fetchContexts]);

  async function handleCreate() {
    if (!newName.trim()) return;
    try {
      await createContext(sessionId, newName.trim(), cloneFrom || undefined);
      setShowCreate(false);
      setNewName("");
      setCloneFrom("");
      await fetchContexts();
    } catch (e: any) {
      alert(e.message || "Error creating context");
    }
  }

  async function handleDelete(cid: string) {
    try {
      await deleteContext(sessionId, cid);
      await fetchContexts();
    } catch (e: any) {
      alert(e.message || "Error deleting context");
    }
  }

  async function handleActivate(cid: string) {
    try {
      await activateContext(sessionId, cid);
      await fetchContexts();
      onActivate?.();
      try {
        const h = await getContextHighlights(sessionId, cid);
        onHighlightsChange?.(h);
      } catch {
        // ignore
      }
    } catch (e: any) {
      alert(e.message || "Error activating context");
    }
  }

  async function handleSetVariable(cid: string, varName: string, value: string) {
    setLoading(true);
    try {
      const updated = await setContextVariable(sessionId, cid, varName, value);
      setContexts((prev) => prev.map((c) => (c.id === cid ? updated : c)));
      const activeCtx = contexts.find((c) => c.id === cid);
      if (activeCtx?.is_active) {
        onActivate?.();
        try {
          const h = await getContextHighlights(sessionId, cid);
          onHighlightsChange?.(h);
        } catch {
          // ignore
        }
      }
    } catch (e: any) {
      alert(e.message || "Error setting variable");
    } finally {
      setLoading(false);
    }
  }

  async function handleCompare() {
    if (compareIds.size < 2) {
      alert("Выберите минимум 2 контекста");
      return;
    }
    try {
      const result = await compareContexts(sessionId, Array.from(compareIds));
      setCompareResult(result);
    } catch (e: any) {
      alert(e.message || "Error comparing contexts");
    }
  }

  function toggleCompare(cid: string) {
    setCompareIds((prev) => {
      const next = new Set(prev);
      if (next.has(cid)) next.delete(cid);
      else next.add(cid);
      return next;
    });
  }

  return (
    <div>
      <h3 className="text-sm font-semibold mb-2">Контексты</h3>

      {contexts.length === 0 && !showCreate && (
        <p className="text-xs text-gray-400 mb-2">Нет контекстов</p>
      )}

      <div className="space-y-1 mb-2">
        {contexts.map((ctx) => (
          <div key={ctx.id} className="border rounded text-xs">
            <div className="flex items-center gap-1 px-2 py-1">
              <input
                type="checkbox"
                checked={compareIds.has(ctx.id)}
                onChange={() => toggleCompare(ctx.id)}
                title="Выбрать для сравнения"
                className="shrink-0"
              />
              <input
                type="radio"
                name="activeCtx"
                checked={ctx.is_active}
                onChange={() => handleActivate(ctx.id)}
                title="Активировать"
                className="shrink-0"
              />
              <button
                className="flex-1 text-left hover:text-blue-600 truncate"
                onClick={() => setExpandedId(expandedId === ctx.id ? null : ctx.id)}
              >
                {ctx.name}
              </button>
              <span className={`shrink-0 px-1 rounded ${ctx.is_complete ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                {ctx.assigned_vars}/{ctx.total_vars}
              </span>
              <button onClick={() => handleDelete(ctx.id)} className="text-red-400 hover:text-red-600 shrink-0" title="Удалить">
                &times;
              </button>
            </div>

            {expandedId === ctx.id && variables && (
              <div className="border-t px-2 py-2 space-y-1 bg-gray-50">
                {variables.map((v) => {
                  const currentValue = ctx.context[v.name] ?? "";
                  return (
                    <div key={v.name} className="flex items-center gap-2">
                      <label className="text-xs text-gray-600 w-20 shrink-0 truncate" title={v.name}>{v.name}</label>
                      {v.domain_type === "enum" && v.values ? (
                        <select
                          value={String(currentValue)}
                          onChange={(e) => handleSetVariable(ctx.id, v.name, e.target.value)}
                          disabled={loading}
                          className="border rounded px-1 py-0.5 text-xs flex-1 disabled:opacity-50"
                        >
                          <option value="">—</option>
                          {v.values.map((val) => (
                            <option key={val} value={val}>{val}</option>
                          ))}
                        </select>
                      ) : v.domain_type === "range" ? (
                        <input
                          type="number"
                          value={String(currentValue)}
                          min={v.min}
                          max={v.max}
                          onChange={(e) => handleSetVariable(ctx.id, v.name, e.target.value)}
                          disabled={loading}
                          className="border rounded px-1 py-0.5 text-xs flex-1 disabled:opacity-50"
                        />
                      ) : (
                        <input
                          type="text"
                          defaultValue={String(currentValue)}
                          onBlur={(e) => {
                            if (e.target.value !== String(currentValue)) {
                              handleSetVariable(ctx.id, v.name, e.target.value);
                            }
                          }}
                          onKeyDown={(e) => {
                            if (e.key === "Enter") handleSetVariable(ctx.id, v.name, (e.target as HTMLInputElement).value);
                          }}
                          disabled={loading}
                          className="border rounded px-1 py-0.5 text-xs flex-1 disabled:opacity-50"
                        />
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        ))}
      </div>

      {compareResult && (
        <div className="mb-2">
          <ContextCompareView data={compareResult} onClose={() => setCompareResult(null)} />
        </div>
      )}

      <div className="flex gap-2">
        {contexts.length >= 2 && (
          <button onClick={handleCompare} disabled={compareIds.size < 2} className="text-xs text-purple-600 hover:underline disabled:opacity-40">
            Сравнить ({compareIds.size})
          </button>
        )}
        {showCreate ? (
          <div className="flex-1 border rounded p-2 bg-gray-50 space-y-1">
            <input
              type="text"
              placeholder="Имя контекста"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") handleCreate(); }}
              className="border rounded px-2 py-1 text-xs w-full"
              autoFocus
            />
            {contexts.length > 0 && (
              <select
                value={cloneFrom}
                onChange={(e) => setCloneFrom(e.target.value)}
                className="border rounded px-2 py-1 text-xs w-full"
              >
                <option value="">Пустой контекст</option>
                {contexts.map((c) => (
                  <option key={c.id} value={c.id}>Клон: {c.name}</option>
                ))}
              </select>
            )}
            <div className="flex gap-2 justify-end">
              <button onClick={() => { setShowCreate(false); setNewName(""); }} className="text-xs text-gray-500 hover:underline">Отмена</button>
              <button onClick={handleCreate} disabled={!newName.trim()} className="text-xs bg-green-600 text-white px-3 py-1 rounded disabled:opacity-50">Создать</button>
            </div>
          </div>
        ) : (
          <button onClick={() => setShowCreate(true)} className="text-xs text-blue-600 hover:underline">
            + Новый контекст
          </button>
        )}
      </div>
    </div>
  );
}

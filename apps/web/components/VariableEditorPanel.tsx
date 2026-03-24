"use client";

import { useState, useEffect, useCallback } from "react";
import { setVariable, listAllVariables, createVariable, updateVariable, deleteVariable } from "@/lib/api";
import { VariableInfo, UserVariableInfo, LoadResponse, GraphPayload } from "@/lib/types";
import { VariableCreateForm } from "./VariableCreateForm";
import { VariableEditForm } from "./VariableEditForm";

type Props = {
  variables: VariableInfo[];
  context: Record<string, any>;
  sessionId: string;
  graph: GraphPayload | null;
  onUpdate: (resp: LoadResponse) => void;
  onUserVariablesChange?: () => void;
  readOnly?: boolean;
};

export function VariableEditorPanel({ variables, context, sessionId, graph, onUpdate, onUserVariablesChange, readOnly }: Props) {
  const [loading, setLoading] = useState<string | null>(null);
  const [userVars, setUserVars] = useState<UserVariableInfo[]>([]);
  const [scenarioOverrides, setScenarioOverrides] = useState<Record<string, UserVariableInfo>>({});
  const [showCreate, setShowCreate] = useState(false);
  const [editingVarId, setEditingVarId] = useState<string | null>(null);
  const [editingScenarioName, setEditingScenarioName] = useState<string | null>(null);

  const fetchUserVars = useCallback(async () => {
    try {
      const all = await listAllVariables(sessionId);
      setUserVars(all.filter((v) => v.origin === "user"));
      const overrides: Record<string, UserVariableInfo> = {};
      for (const v of all) {
        if (v.origin === "scenario" && v.id) {
          overrides[v.name] = v;
        }
      }
      setScenarioOverrides(overrides);
    } catch {
      // ignore
    }
  }, [sessionId]);

  useEffect(() => {
    fetchUserVars();
  }, [fetchUserVars]);

  async function handleChange(varName: string, value: string | null) {
    setLoading(varName);
    try {
      const resp = await setVariable(sessionId, varName, value);
      onUpdate(resp);
    } catch (e: any) {
      alert(e.message || "Error setting variable");
    } finally {
      setLoading(null);
    }
  }

  async function handleCreate(data: { name: string; type_tag?: string; domain_type: string; domain: Record<string, any> }) {
    try {
      await createVariable(sessionId, data);
      setShowCreate(false);
      await fetchUserVars();
      onUserVariablesChange?.();
    } catch (e: any) {
      alert(e.message || "Error creating variable");
    }
  }

  async function handleDelete(id: string) {
    try {
      await deleteVariable(sessionId, id);
      await fetchUserVars();
      onUserVariablesChange?.();
    } catch (e: any) {
      alert(e.message || "Error deleting variable");
    }
  }

  async function handleEdit(id: string, data: { name?: string; type_tag?: string; domain_type?: string; domain?: Record<string, any> }) {
    try {
      await updateVariable(sessionId, id, data);
      setEditingVarId(null);
      await fetchUserVars();
      onUserVariablesChange?.();
    } catch (e: any) {
      alert(e.message || "Error updating variable");
    }
  }

  async function handleEditScenario(v: VariableInfo, data: { name?: string; type_tag?: string; domain_type?: string; domain?: Record<string, any> }) {
    try {
      const override = scenarioOverrides[v.name];
      if (override?.id) {
        await updateVariable(sessionId, override.id, data);
      } else {
        await createVariable(sessionId, {
          name: data.name || v.name,
          type_tag: data.type_tag,
          domain_type: data.domain_type || v.domain_type,
          domain: data.domain || {},
        });
      }
      setEditingScenarioName(null);
      await fetchUserVars();
      onUserVariablesChange?.();
    } catch (e: any) {
      alert(e.message || "Error updating variable");
    }
  }

  if (!variables?.length && userVars.length === 0 && !showCreate) return null;

  return (
    <div>
      <h3 className="text-sm font-semibold mb-2">Переменные</h3>

      {variables && variables.length > 0 && (
        <div className="mb-3">
          <div className="text-xs text-gray-400 mb-1">Сценарий</div>
          <div className="space-y-2">
            {variables.map((v) => {
              const override = scenarioOverrides[v.name];
              const effectiveVar = override ?? v;
              const domainType = effectiveVar.domain_type;
              const values = effectiveVar.values ?? v.values;
              const min = effectiveVar.min ?? v.min;
              const max = effectiveVar.max ?? v.max;

              if (editingScenarioName === v.name) {
                const editData: UserVariableInfo = override ?? {
                  name: v.name,
                  type_tag: v.type_tag,
                  domain_type: v.domain_type,
                  values: v.values,
                  min: v.min,
                  max: v.max,
                  origin: "scenario",
                  domain: v.domain_type === "enum" ? { values: v.values ?? [] }
                    : v.domain_type === "range" ? { min: v.min ?? 0, max: v.max ?? 100 }
                    : { name: "custom" },
                };
                return (
                  <VariableEditForm
                    key={v.name}
                    variable={editData}
                    graph={graph}
                    onSubmit={(data) => handleEditScenario(v, data)}
                    onCancel={() => setEditingScenarioName(null)}
                  />
                );
              }

              const currentValue = context[v.name] ?? "";
              const isLoading = loading === v.name;
              return (
                <div key={v.name} className="flex items-center gap-2">
                  <label className="text-xs text-gray-600 w-20 shrink-0 truncate" title={v.name}>
                    {v.name}
                  </label>
                  {domainType === "enum" && values ? (
                    <select
                      value={String(currentValue)}
                      onChange={(e) => handleChange(v.name, e.target.value || null)}
                      disabled={isLoading || readOnly}
                      className="border rounded px-2 py-1 text-sm flex-1 disabled:opacity-50"
                    >
                      <option value="">—</option>
                      {values.map((val) => (
                        <option key={val} value={val}>{val}</option>
                      ))}
                    </select>
                  ) : domainType === "range" ? (
                    <input
                      type="number"
                      value={String(currentValue)}
                      min={min}
                      max={max}
                      onChange={(e) => handleChange(v.name, e.target.value)}
                      disabled={isLoading || readOnly}
                      className="border rounded px-2 py-1 text-sm flex-1 disabled:opacity-50"
                    />
                  ) : (
                    <input
                      type="text"
                      value={String(currentValue)}
                      onBlur={(e) => {
                        if (e.target.value !== String(currentValue)) {
                          handleChange(v.name, e.target.value);
                        }
                      }}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") handleChange(v.name, (e.target as HTMLInputElement).value);
                      }}
                      disabled={isLoading || readOnly}
                      className="border rounded px-2 py-1 text-sm flex-1 disabled:opacity-50"
                    />
                  )}
                  {isLoading && <span className="text-xs text-gray-400">...</span>}
                  {!readOnly && (
                    <button
                      onClick={() => setEditingScenarioName(v.name)}
                      className="text-gray-400 hover:text-yellow-600 text-sm"
                      title="Редактировать"
                    >
                      &#9998;
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {userVars.length > 0 && (
        <div className="mb-3">
          <div className="text-xs text-gray-400 mb-1">Пользовательские</div>
          <div className="space-y-1">
            {userVars.map((uv) => {
              if (editingVarId === uv.id) {
                return (
                  <VariableEditForm
                    key={uv.id}
                    variable={uv}
                    graph={graph}
                    onSubmit={(data) => uv.id && handleEdit(uv.id, data)}
                    onCancel={() => setEditingVarId(null)}
                  />
                );
              }
              const currentValue = context[uv.name] ?? "";
              const isLoading = loading === uv.name;
              return (
                <div key={uv.id} className="flex items-center gap-2">
                  <label className="text-xs text-gray-600 w-20 shrink-0 truncate" title={uv.name}>
                    {uv.name}
                  </label>
                  {uv.domain_type === "enum" && uv.values ? (
                    <select
                      value={String(currentValue)}
                      onChange={(e) => handleChange(uv.name, e.target.value || null)}
                      disabled={isLoading || readOnly}
                      className="border rounded px-2 py-1 text-sm flex-1 disabled:opacity-50"
                    >
                      <option value="">—</option>
                      {uv.values.map((val) => (
                        <option key={val} value={val}>{val}</option>
                      ))}
                    </select>
                  ) : uv.domain_type === "range" ? (
                    <input
                      type="number"
                      value={String(currentValue)}
                      min={uv.min}
                      max={uv.max}
                      onChange={(e) => handleChange(uv.name, e.target.value)}
                      disabled={isLoading || readOnly}
                      className="border rounded px-2 py-1 text-sm flex-1 disabled:opacity-50"
                    />
                  ) : (
                    <input
                      type="text"
                      value={String(currentValue)}
                      onBlur={(e) => {
                        if (e.target.value !== String(currentValue)) {
                          handleChange(uv.name, e.target.value);
                        }
                      }}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") handleChange(uv.name, (e.target as HTMLInputElement).value);
                      }}
                      disabled={isLoading || readOnly}
                      className="border rounded px-2 py-1 text-sm flex-1 disabled:opacity-50"
                    />
                  )}
                  {isLoading && <span className="text-xs text-gray-400">...</span>}
                  {!readOnly && (
                    <>
                      <button
                        onClick={() => uv.id && setEditingVarId(uv.id)}
                        className="text-gray-400 hover:text-yellow-600 text-sm"
                        title="Редактировать"
                      >
                        &#9998;
                      </button>
                      <button
                        onClick={() => uv.id && handleDelete(uv.id)}
                        className="text-red-400 hover:text-red-600 text-sm"
                        title="Удалить"
                      >
                        &times;
                      </button>
                    </>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {!readOnly && (showCreate ? (
        <VariableCreateForm
          graph={graph}
          onSubmit={handleCreate}
          onCancel={() => setShowCreate(false)}
        />
      ) : (
        <button
          onClick={() => setShowCreate(true)}
          className="text-xs text-blue-600 hover:underline"
        >
          + Новая переменная
        </button>
      ))}
    </div>
  );
}

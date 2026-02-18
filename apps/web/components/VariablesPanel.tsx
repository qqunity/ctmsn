"use client";

import { useState } from "react";
import { setVariable } from "@/lib/api";
import { VariableInfo, LoadResponse } from "@/lib/types";

type Props = {
  variables: VariableInfo[];
  context: Record<string, any>;
  sessionId: string;
  onUpdate: (resp: LoadResponse) => void;
};

export function VariablesPanel({ variables, context, sessionId, onUpdate }: Props) {
  const [loading, setLoading] = useState<string | null>(null);

  async function handleChange(varName: string, value: string) {
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

  if (!variables || variables.length === 0) return null;

  return (
    <div>
      <h3 className="text-sm font-semibold mb-2">Переменные</h3>
      <div className="space-y-2">
        {variables.map((v) => {
          const currentValue = context[v.name] ?? "";
          const isLoading = loading === v.name;

          return (
            <div key={v.name} className="flex items-center gap-2">
              <label className="text-xs text-gray-600 w-20 shrink-0 truncate" title={v.name}>
                {v.name}
              </label>
              {v.domain_type === "enum" && v.values ? (
                <select
                  value={String(currentValue)}
                  onChange={(e) => handleChange(v.name, e.target.value)}
                  disabled={isLoading}
                  className="border rounded px-2 py-1 text-sm flex-1 disabled:opacity-50"
                >
                  <option value="">—</option>
                  {v.values.map((val) => (
                    <option key={val} value={val}>
                      {val}
                    </option>
                  ))}
                </select>
              ) : v.domain_type === "range" ? (
                <input
                  type="number"
                  value={String(currentValue)}
                  min={v.min}
                  max={v.max}
                  onChange={(e) => handleChange(v.name, e.target.value)}
                  disabled={isLoading}
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
                    if (e.key === "Enter") {
                      handleChange(v.name, (e.target as HTMLInputElement).value);
                    }
                  }}
                  disabled={isLoading}
                  className="border rounded px-2 py-1 text-sm flex-1 disabled:opacity-50"
                />
              )}
              {isLoading && <span className="text-xs text-gray-400">...</span>}
            </div>
          );
        })}
      </div>
    </div>
  );
}

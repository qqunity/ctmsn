"use client";

import { useState } from "react";
import { TermRef, GraphPayload, VariableInfo } from "@/lib/types";

type Props = {
  value: TermRef | null;
  onChange: (term: TermRef) => void;
  graph: GraphPayload | null;
  variables: VariableInfo[];
  pickerId: string;
  activeTermPickerId: string | null;
  onFocus: (id: string | null) => void;
};

export function TermPicker({ value, onChange, graph, variables, pickerId, activeTermPickerId, onFocus }: Props) {
  const [mode, setMode] = useState<"concept" | "variable" | "literal">(value?.kind ?? "concept");
  const isActive = activeTermPickerId === pickerId;

  const conceptIds = graph?.nodes?.map((n) => n.id) ?? [];
  const varNames = variables?.map((v) => v.name) ?? [];

  return (
    <div className={`border rounded px-1 py-0.5 text-xs ${isActive ? "ring-2 ring-blue-400" : ""}`}>
      <div className="flex gap-1 mb-0.5">
        {(["concept", "variable", "literal"] as const).map((m) => (
          <button
            key={m}
            onClick={() => setMode(m)}
            className={`px-1 rounded ${mode === m ? "bg-blue-100 text-blue-700" : "text-gray-400 hover:text-gray-600"}`}
          >
            {m === "concept" ? "C" : m === "variable" ? "V" : "L"}
          </button>
        ))}
      </div>

      {mode === "concept" && (
        <div className="flex gap-1">
          <select
            value={value?.kind === "concept" ? value.id : ""}
            onChange={(e) => { if (e.target.value) onChange({ kind: "concept", id: e.target.value }); }}
            className="border rounded px-1 py-0.5 text-xs flex-1"
          >
            <option value="">—</option>
            {conceptIds.map((cid) => (
              <option key={cid} value={cid}>{cid}</option>
            ))}
          </select>
          <button
            onClick={() => onFocus(isActive ? null : pickerId)}
            className={`px-1 rounded text-xs ${isActive ? "bg-blue-500 text-white" : "bg-gray-100 hover:bg-gray-200"}`}
            title="Выбрать на графе"
          >
            &#8982;
          </button>
        </div>
      )}

      {mode === "variable" && (
        <select
          value={value?.kind === "variable" ? value.name : ""}
          onChange={(e) => { if (e.target.value) onChange({ kind: "variable", name: e.target.value }); }}
          className="border rounded px-1 py-0.5 text-xs w-full"
        >
          <option value="">—</option>
          {varNames.map((name) => (
            <option key={name} value={name}>{name}</option>
          ))}
        </select>
      )}

      {mode === "literal" && (
        <input
          type="text"
          value={value?.kind === "literal" ? String(value.value) : ""}
          onChange={(e) => onChange({ kind: "literal", value: e.target.value })}
          placeholder="Значение"
          className="border rounded px-1 py-0.5 text-xs w-full"
        />
      )}
    </div>
  );
}

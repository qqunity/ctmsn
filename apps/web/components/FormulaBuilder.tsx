"use client";

import { useCallback } from "react";
import { FormulaNode, TermRef, GraphPayload, VariableInfo, Predicate } from "@/lib/types";
import { TermPicker } from "./TermPicker";

type Props = {
  value: FormulaNode;
  onChange: (node: FormulaNode) => void;
  graph: GraphPayload | null;
  variables: VariableInfo[];
  activeTermPickerId: string | null;
  onTermPickerFocus: (id: string | null) => void;
  path?: string;
};

const FORMULA_TYPES = ["FactAtom", "EqAtom", "Not", "And", "Or", "Implies"] as const;

function emptyFormula(type: string): FormulaNode {
  switch (type) {
    case "FactAtom": return { type: "FactAtom", predicate: "", args: [] };
    case "EqAtom": return { type: "EqAtom", left: { kind: "concept", id: "" }, right: { kind: "concept", id: "" } };
    case "Not": return { type: "Not", inner: { type: "FactAtom", predicate: "", args: [] } };
    case "And": return { type: "And", items: [{ type: "FactAtom", predicate: "", args: [] }] };
    case "Or": return { type: "Or", items: [{ type: "FactAtom", predicate: "", args: [] }] };
    case "Implies": return { type: "Implies", left: { type: "FactAtom", predicate: "", args: [] }, right: { type: "FactAtom", predicate: "", args: [] } };
    default: return { type: "FactAtom", predicate: "", args: [] };
  }
}

function formulaToText(node: FormulaNode): string {
  switch (node.type) {
    case "FactAtom": {
      const args = node.args.map(termToText).join(", ");
      return `FactAtom("${node.predicate}", ${args})`;
    }
    case "EqAtom":
      return `EqAtom(${termToText(node.left)}, ${termToText(node.right)})`;
    case "Not":
      return `Not(${formulaToText(node.inner)})`;
    case "And":
      return `And(${node.items.map(formulaToText).join(", ")})`;
    case "Or":
      return `Or(${node.items.map(formulaToText).join(", ")})`;
    case "Implies":
      return `Implies(${formulaToText(node.left)}, ${formulaToText(node.right)})`;
  }
}

function termToText(t: TermRef): string {
  if (t.kind === "concept") return t.id || "?";
  if (t.kind === "variable") return t.name || "?";
  return String(t.value);
}

export { formulaToText };

export function FormulaBuilder({ value, onChange, graph, variables, activeTermPickerId, onTermPickerFocus, path = "root" }: Props) {
  const predicates: Predicate[] = graph?.predicates ?? [];

  const handleTypeChange = useCallback((type: string) => {
    onChange(emptyFormula(type));
  }, [onChange]);

  function updateArg(idx: number, term: TermRef) {
    if (value.type !== "FactAtom") return;
    const newArgs = [...value.args];
    newArgs[idx] = term;
    onChange({ ...value, args: newArgs });
  }

  function handlePredicateChange(predName: string) {
    if (value.type !== "FactAtom") return;
    const pred = predicates.find((p) => p.name === predName);
    const arity = pred?.arity ?? 2;
    const args: TermRef[] = [];
    for (let i = 0; i < arity; i++) {
      args.push(value.args[i] ?? { kind: "concept", id: "" });
    }
    onChange({ ...value, predicate: predName, args });
  }

  return (
    <div className="border rounded p-2 bg-white space-y-1">
      <select
        value={value.type}
        onChange={(e) => handleTypeChange(e.target.value)}
        className="border rounded px-1 py-0.5 text-xs font-medium"
      >
        {FORMULA_TYPES.map((t) => (
          <option key={t} value={t}>{t}</option>
        ))}
      </select>

      {value.type === "FactAtom" && (
        <div className="space-y-1 pl-2">
          <select
            value={value.predicate}
            onChange={(e) => handlePredicateChange(e.target.value)}
            className="border rounded px-1 py-0.5 text-xs w-full"
          >
            <option value="">Предикат...</option>
            {predicates.map((p) => (
              <option key={p.name} value={p.name}>{p.name} (арн. {p.arity})</option>
            ))}
          </select>
          {value.args.map((arg, idx) => (
            <div key={idx} className="flex items-center gap-1">
              <span className="text-xs text-gray-400 w-8">arg{idx}</span>
              <TermPicker
                value={arg}
                onChange={(t) => updateArg(idx, t)}
                graph={graph}
                variables={variables}
                pickerId={`${path}.args.${idx}`}
                activeTermPickerId={activeTermPickerId}
                onFocus={onTermPickerFocus}
              />
            </div>
          ))}
        </div>
      )}

      {value.type === "EqAtom" && (
        <div className="space-y-1 pl-2">
          <div className="flex items-center gap-1">
            <span className="text-xs text-gray-400 w-8">left</span>
            <TermPicker
              value={value.left}
              onChange={(t) => onChange({ ...value, left: t })}
              graph={graph}
              variables={variables}
              pickerId={`${path}.left`}
              activeTermPickerId={activeTermPickerId}
              onFocus={onTermPickerFocus}
            />
          </div>
          <div className="flex items-center gap-1">
            <span className="text-xs text-gray-400 w-8">right</span>
            <TermPicker
              value={value.right}
              onChange={(t) => onChange({ ...value, right: t })}
              graph={graph}
              variables={variables}
              pickerId={`${path}.right`}
              activeTermPickerId={activeTermPickerId}
              onFocus={onTermPickerFocus}
            />
          </div>
        </div>
      )}

      {value.type === "Not" && (
        <div className="pl-2">
          <FormulaBuilder
            value={value.inner}
            onChange={(inner) => onChange({ ...value, inner })}
            graph={graph}
            variables={variables}
            activeTermPickerId={activeTermPickerId}
            onTermPickerFocus={onTermPickerFocus}
            path={`${path}.inner`}
          />
        </div>
      )}

      {(value.type === "And" || value.type === "Or") && (
        <div className="pl-2 space-y-1">
          {value.items.map((item, idx) => (
            <div key={idx} className="flex gap-1">
              <div className="flex-1">
                <FormulaBuilder
                  value={item}
                  onChange={(updated) => {
                    const newItems = [...value.items];
                    newItems[idx] = updated;
                    onChange({ ...value, items: newItems });
                  }}
                  graph={graph}
                  variables={variables}
                  activeTermPickerId={activeTermPickerId}
                  onTermPickerFocus={onTermPickerFocus}
                  path={`${path}.items.${idx}`}
                />
              </div>
              {value.items.length > 1 && (
                <button
                  onClick={() => onChange({ ...value, items: value.items.filter((_, i) => i !== idx) })}
                  className="text-red-400 hover:text-red-600 text-xs self-start mt-1"
                >
                  &times;
                </button>
              )}
            </div>
          ))}
          <button
            onClick={() => onChange({ ...value, items: [...value.items, { type: "FactAtom", predicate: "", args: [] }] })}
            className="text-xs text-blue-600 hover:underline"
          >
            + Добавить
          </button>
        </div>
      )}

      {value.type === "Implies" && (
        <div className="pl-2 space-y-1">
          <div>
            <span className="text-xs text-gray-400">if:</span>
            <FormulaBuilder
              value={value.left}
              onChange={(left) => onChange({ ...value, left })}
              graph={graph}
              variables={variables}
              activeTermPickerId={activeTermPickerId}
              onTermPickerFocus={onTermPickerFocus}
              path={`${path}.left`}
            />
          </div>
          <div>
            <span className="text-xs text-gray-400">then:</span>
            <FormulaBuilder
              value={value.right}
              onChange={(right) => onChange({ ...value, right })}
              graph={graph}
              variables={variables}
              activeTermPickerId={activeTermPickerId}
              onTermPickerFocus={onTermPickerFocus}
              path={`${path}.right`}
            />
          </div>
        </div>
      )}

      <div className="text-[10px] text-gray-400 font-mono truncate pt-1 border-t">
        {formulaToText(value)}
      </div>
    </div>
  );
}

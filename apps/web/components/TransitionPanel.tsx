"use client";

import { useCallback, useEffect, useState } from "react";
import {
  listTransitionRules,
  createTransitionRule,
  deleteTransitionRule,
  runTransition,
} from "@/lib/api";
import {
  FormulaInfo,
  FormulaNode,
  GraphPayload,
  VariableInfo,
  TransitionEffectOp,
  TransitionRuleInfo,
  TransitionRunResult,
} from "@/lib/types";
import { FormulaBuilder } from "./FormulaBuilder";

type Props = {
  sessionId: string;
  graph: GraphPayload | null;
  variables: VariableInfo[];
  formulas: FormulaInfo[];
  activeTermPickerId: string | null;
  onTermPickerFocus: (id: string | null) => void;
  onStepHighlight: (touched: string[]) => void;
};

const EMPTY_GUARD: FormulaNode = { type: "FactAtom", predicate: "", args: [] };

export function TransitionPanel({
  sessionId,
  graph,
  variables,
  formulas,
  activeTermPickerId,
  onTermPickerFocus,
  onStepHighlight,
}: Props) {
  const [rules, setRules] = useState<TransitionRuleInfo[]>([]);
  const [showEditor, setShowEditor] = useState(false);
  const [name, setName] = useState("");
  const [guard, setGuard] = useState<FormulaNode>(EMPTY_GUARD);
  const [effect, setEffect] = useState<TransitionEffectOp[]>([]);
  const [priority, setPriority] = useState(0);

  const [invariantIds, setInvariantIds] = useState<Set<string>>(new Set());
  const [maxSteps, setMaxSteps] = useState(50);
  const [result, setResult] = useState<TransitionRunResult | null>(null);
  const [activeStep, setActiveStep] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  const predicates = graph?.predicates ?? [];

  const refresh = useCallback(async () => {
    try {
      setRules(await listTransitionRules(sessionId));
    } catch {
      /* ignore */
    }
  }, [sessionId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  function addEffectOp() {
    setEffect((prev) => [...prev, { op: "add", predicate: "", args: [] }]);
  }

  function updateEffectOp(idx: number, patch: Partial<TransitionEffectOp>) {
    setEffect((prev) => {
      const next = [...prev];
      const merged = { ...next[idx], ...patch };
      if (patch.predicate !== undefined) {
        const arity = predicates.find((p) => p.name === patch.predicate)?.arity ?? merged.args.length;
        const args = [...merged.args];
        args.length = arity;
        merged.args = Array.from(args, (a) => a ?? "");
      }
      next[idx] = merged;
      return next;
    });
  }

  function updateEffectArg(idx: number, argIdx: number, value: string) {
    setEffect((prev) => {
      const next = [...prev];
      const args = [...next[idx].args];
      args[argIdx] = value;
      next[idx] = { ...next[idx], args };
      return next;
    });
  }

  function removeEffectOp(idx: number) {
    setEffect((prev) => prev.filter((_, i) => i !== idx));
  }

  async function handleSaveRule() {
    if (!name.trim()) {
      alert("Укажите имя правила");
      return;
    }
    try {
      await createTransitionRule(sessionId, { name: name.trim(), guard, effect, priority });
      setName("");
      setGuard(EMPTY_GUARD);
      setEffect([]);
      setPriority(0);
      setShowEditor(false);
      await refresh();
    } catch (e: any) {
      alert(e.message || "Ошибка сохранения правила");
    }
  }

  async function handleDelete(id: string) {
    await deleteTransitionRule(sessionId, id);
    await refresh();
  }

  function toggleInvariant(fid: string) {
    setInvariantIds((prev) => {
      const next = new Set(prev);
      if (next.has(fid)) next.delete(fid);
      else next.add(fid);
      return next;
    });
  }

  async function handleRun() {
    setLoading(true);
    setActiveStep(null);
    onStepHighlight([]);
    try {
      const res = await runTransition(sessionId, {
        invariant_ids: Array.from(invariantIds),
        max_steps: maxSteps,
      });
      setResult(res);
    } catch (e: any) {
      alert(e.message || "Ошибка запуска переходов");
    } finally {
      setLoading(false);
    }
  }

  function selectStep(idx: number) {
    setActiveStep(idx);
    const step = result?.steps[idx];
    onStepHighlight(step ? step.touched : []);
  }

  return (
    <div data-testid="transition-panel">
      <h3 className="text-sm font-semibold mb-2">Переходы (режимы)</h3>

      {/* Rules list */}
      <div className="mb-2">
        <div className="flex items-center justify-between mb-1">
          <label className="text-xs text-gray-500">Правила переходов ({rules.length})</label>
          <button
            onClick={() => setShowEditor((s) => !s)}
            className="text-xs text-blue-600 hover:underline"
          >
            {showEditor ? "Отмена" : "+ Правило"}
          </button>
        </div>
        {rules.length > 0 && (
          <div className="space-y-0.5 max-h-32 overflow-auto border rounded p-1">
            {rules.map((r) => (
              <div key={r.id} className="flex items-center gap-1.5 text-xs">
                <span className="font-medium">{r.name}</span>
                <span className="text-gray-400 font-mono text-[10px] truncate flex-1">{r.guard_text}</span>
                <button
                  onClick={() => handleDelete(r.id)}
                  className="text-red-400 hover:text-red-600"
                  title="Удалить"
                >
                  &times;
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Rule editor */}
      {showEditor && (
        <div className="mb-3 border rounded bg-gray-50 p-2 space-y-2">
          <input
            type="text"
            placeholder="Имя правила"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="border rounded px-2 py-1 text-xs w-full"
            data-testid="rule-name"
          />
          <div>
            <label className="text-xs text-gray-500 block mb-0.5">Гвард (условие)</label>
            <FormulaBuilder
              value={guard}
              onChange={setGuard}
              graph={graph}
              variables={variables}
              activeTermPickerId={activeTermPickerId}
              onTermPickerFocus={onTermPickerFocus}
              path="transition-guard"
            />
          </div>
          <div>
            <div className="flex items-center justify-between mb-0.5">
              <label className="text-xs text-gray-500">Эффект</label>
              <button onClick={addEffectOp} className="text-xs text-blue-600 hover:underline">
                + Операция
              </button>
            </div>
            <div className="space-y-1">
              {effect.map((op, idx) => (
                <div key={idx} className="flex flex-wrap items-center gap-1 border rounded p-1 bg-white">
                  <select
                    value={op.op}
                    onChange={(e) => updateEffectOp(idx, { op: e.target.value as "add" | "retract" })}
                    className="border rounded px-1 py-0.5 text-xs"
                  >
                    <option value="add">add</option>
                    <option value="retract">retract</option>
                  </select>
                  <select
                    value={op.predicate}
                    onChange={(e) => updateEffectOp(idx, { predicate: e.target.value })}
                    className="border rounded px-1 py-0.5 text-xs"
                  >
                    <option value="">предикат...</option>
                    {predicates.map((p) => (
                      <option key={p.name} value={p.name}>{p.name} ({p.arity})</option>
                    ))}
                  </select>
                  {op.args.map((arg, argIdx) => (
                    <input
                      key={argIdx}
                      type="text"
                      placeholder={`arg${argIdx}`}
                      value={String(arg ?? "")}
                      onChange={(e) => updateEffectArg(idx, argIdx, e.target.value)}
                      className="border rounded px-1 py-0.5 text-xs w-16"
                    />
                  ))}
                  <button onClick={() => removeEffectOp(idx)} className="text-red-400 hover:text-red-600 text-xs">
                    &times;
                  </button>
                </div>
              ))}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <label className="text-xs text-gray-500">Приоритет</label>
            <input
              type="number"
              value={priority}
              onChange={(e) => setPriority(parseInt(e.target.value) || 0)}
              className="border rounded px-1 py-0.5 text-xs w-16"
            />
          </div>
          <button
            onClick={handleSaveRule}
            className="text-xs bg-green-600 text-white px-3 py-1 rounded"
            data-testid="save-rule"
          >
            Сохранить правило
          </button>
        </div>
      )}

      {/* Invariants */}
      <div className="mb-2">
        <label className="text-xs text-gray-500 block mb-0.5">Инварианты (формулы)</label>
        {formulas.length === 0 ? (
          <p className="text-xs text-gray-400">Нет формул в библиотеке</p>
        ) : (
          <div className="space-y-0.5 max-h-28 overflow-auto border rounded p-1">
            {formulas.map((f) => (
              <label key={f.id} className="flex items-start gap-1.5 text-xs cursor-pointer hover:bg-gray-50 px-1 py-0.5 rounded">
                <input
                  type="checkbox"
                  checked={invariantIds.has(f.id)}
                  onChange={() => toggleInvariant(f.id)}
                  className="mt-0.5 shrink-0"
                />
                <span>
                  <span className="font-medium">{f.name}</span>
                  <span className="text-gray-400 ml-1 font-mono text-[10px]">{f.text}</span>
                </span>
              </label>
            ))}
          </div>
        )}
      </div>

      {/* Run */}
      <div className="flex items-center gap-2 mb-2">
        <button
          onClick={handleRun}
          disabled={loading || rules.length === 0}
          className="text-xs bg-indigo-600 text-white px-3 py-1 rounded disabled:opacity-50"
          data-testid="run-transition"
        >
          Выполнить переходы
        </button>
        <label className="text-xs text-gray-500">шагов ≤</label>
        <input
          type="number"
          value={maxSteps}
          onChange={(e) => setMaxSteps(parseInt(e.target.value) || 50)}
          className="border rounded px-1 py-0.5 text-xs w-14"
        />
      </div>

      {/* Result */}
      {result && (
        <div data-testid="transition-result">
          <div
            className={`text-xs px-2 py-1 rounded mb-1 font-semibold ${
              result.final_mode === "stable" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"
            }`}
            data-testid="final-mode"
          >
            {result.final_mode === "stable"
              ? `Устойчивый режим за ${result.convergence_steps} шаг(ов)`
              : "Переходный режим (устойчивость не достигнута)"}
          </div>
          <div className="space-y-0.5 max-h-48 overflow-auto border rounded p-1">
            {result.steps.length === 0 && (
              <p className="text-xs text-gray-400">Переходов не выполнено (уже устойчиво)</p>
            )}
            {result.steps.map((s) => (
              <button
                key={s.index}
                onClick={() => selectStep(s.index)}
                className={`w-full text-left text-xs px-1 py-0.5 rounded hover:bg-gray-50 ${
                  activeStep === s.index ? "bg-blue-50 ring-1 ring-blue-300" : ""
                }`}
              >
                <span className="font-medium">шаг {s.index}: {s.rule}</span>
                <span
                  className={`ml-1 px-1 rounded text-[10px] ${
                    s.mode === "stable" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"
                  }`}
                >
                  {s.mode}
                </span>
                {!s.invariants_ok && (
                  <span className="ml-1 px-1 rounded text-[10px] bg-red-100 text-red-700">инвариант!</span>
                )}
                <span className="block text-gray-400 font-mono text-[10px]">
                  {s.added.map((a) => `+${a}`).concat(s.removed.map((r) => `-${r}`)).join(" ")}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

"use client";

import { useState } from "react";
import { runForcingCheck, runForcingForces } from "@/lib/api";
import {
  FormulaInfo,
  NamedContextInfo,
  ForcingCheckResult,
  ForcingForcesResult,
  ForcingRunRecord,
} from "@/lib/types";

type Props = {
  sessionId: string;
  formulas: FormulaInfo[];
  contexts: NamedContextInfo[];
  scenarioCheck?: string | null;
  scenarioForces?: string | null;
  scenarioForce?: string | null;
};

const RESULT_COLORS: Record<string, string> = {
  true: "bg-green-100 text-green-700",
  false: "bg-red-100 text-red-700",
  unknown: "bg-yellow-100 text-yellow-700",
};

const RESULT_LABELS: Record<string, string> = {
  true: "TRUE",
  false: "FALSE",
  unknown: "UNKNOWN",
};

function parseCheckOk(value: string): boolean {
  // Handle "CheckResult(ok=True, ...)" or simple "ok" / "fail"
  const m = value.match(/ok=(True|False)/i);
  if (m) return m[1].toLowerCase() === "true";
  return value.toLowerCase() === "ok";
}

function parseTribool(value: string): string {
  // Handle "ForceResult(status=<TriBool.TRUE: 'true'>, ...)"
  const statusMatch = value.match(/status=<(?:TriBool\.)?(\w+):/i);
  if (statusMatch) return statusMatch[1].toUpperCase();
  // Handle "TriBool.TRUE" or plain "TRUE"
  return value.replace(/^.*TriBool\./i, "").replace(/[^A-Za-z].*/s, "").toUpperCase();
}

function triboolColors(normalized: string): string {
  if (normalized === "TRUE") return "bg-green-100 text-green-700";
  if (normalized === "FALSE") return "bg-red-100 text-red-700";
  if (normalized === "UNKNOWN") return "bg-yellow-100 text-yellow-700";
  return "bg-gray-100 text-gray-700";
}

function scenarioBadge(value: string | null | undefined, type: "check" | "tribool") {
  if (!value) return <span className="text-xs text-gray-400">—</span>;
  if (type === "check") {
    const isOk = parseCheckOk(value);
    return (
      <span className={`px-1.5 py-0.5 rounded text-xs font-semibold ${isOk ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
        {isOk ? "ok" : "fail"}
      </span>
    );
  }
  // tribool
  const normalized = parseTribool(value);
  return (
    <span className={`px-1.5 py-0.5 rounded text-xs font-semibold ${triboolColors(normalized)}`}>
      {normalized}
    </span>
  );
}

export function ForcingPanel({ sessionId, formulas, contexts, scenarioCheck, scenarioForces, scenarioForce }: Props) {
  const [contextId, setContextId] = useState<string>("");
  const [selectedConditions, setSelectedConditions] = useState<Set<string>>(new Set());
  const [phiId, setPhiId] = useState<string>("");

  const [checkResult, setCheckResult] = useState<ForcingCheckResult | null>(null);
  const [forcesResult, setForcesResult] = useState<ForcingForcesResult | null>(null);
  const [showExplanation, setShowExplanation] = useState(false);
  const [history, setHistory] = useState<ForcingRunRecord[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [loading, setLoading] = useState(false);

  function toggleCondition(fid: string) {
    setSelectedConditions((prev) => {
      const next = new Set(prev);
      if (next.has(fid)) next.delete(fid);
      else next.add(fid);
      return next;
    });
  }

  function addToHistory(type: "check" | "forces", resultSummary: string, condNames: string[], phiName: string | null) {
    const ctxName = contextId
      ? contexts.find((c) => c.id === contextId)?.name ?? "?"
      : "Активный контекст";
    const record: ForcingRunRecord = {
      id: crypto.randomUUID(),
      timestamp: new Date().toLocaleTimeString(),
      type,
      context_name: ctxName,
      condition_names: condNames,
      phi_name: phiName,
      result_summary: resultSummary,
    };
    setHistory((prev) => [record, ...prev].slice(0, 20));
  }

  async function handleCheck() {
    setLoading(true);
    setForcesResult(null);
    try {
      const condIds = Array.from(selectedConditions);
      const res = await runForcingCheck(sessionId, {
        context_id: contextId || null,
        condition_ids: condIds,
      });
      setCheckResult(res);
      const condNames = condIds.map((id) => formulas.find((f) => f.id === id)?.name ?? "?");
      addToHistory("check", res.ok ? "ok" : "false", condNames, null);
    } catch (e: any) {
      alert(e.message || "Error running check");
    } finally {
      setLoading(false);
    }
  }

  async function handleForces() {
    setLoading(true);
    setCheckResult(null);
    setShowExplanation(false);
    try {
      const condIds = Array.from(selectedConditions);
      const res = await runForcingForces(sessionId, {
        context_id: contextId || null,
        condition_ids: condIds,
        phi_id: phiId,
      });
      setForcesResult(res);
      const condNames = condIds.map((id) => formulas.find((f) => f.id === id)?.name ?? "?");
      addToHistory("forces", res.result, condNames, res.phi_name);
    } catch (e: any) {
      alert(e.message || "Error running forces");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h3 className="text-sm font-semibold mb-2">Форсирование</h3>

      {/* Scenario run results */}
      {(scenarioCheck || scenarioForces || scenarioForce) && (
        <div className="mb-3 border rounded bg-gray-50 p-2">
          <div className="text-xs font-medium text-gray-500 mb-1">Результат сценария</div>
          <div className="space-y-1">
            {scenarioCheck != null && (
              <div className="flex items-center gap-2 text-xs">
                <span className="text-gray-500 w-12">check:</span>
                {scenarioBadge(scenarioCheck, "check")}
              </div>
            )}
            {scenarioForces != null && (
              <div className="flex items-center gap-2 text-xs">
                <span className="text-gray-500 w-12">forces:</span>
                {scenarioBadge(scenarioForces, "tribool")}
              </div>
            )}
            {scenarioForce != null && (
              <div className="flex items-center gap-2 text-xs">
                <span className="text-gray-500 w-12">force:</span>
                {scenarioBadge(scenarioForce, "tribool")}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Context selector */}
      <div className="mb-2">
        <label className="text-xs text-gray-500 block mb-0.5">Контекст</label>
        <select
          value={contextId}
          onChange={(e) => setContextId(e.target.value)}
          className="border rounded px-2 py-1 text-xs w-full"
        >
          <option value="">Активный контекст</option>
          {contexts.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
      </div>

      {/* Conditions (checkboxes) */}
      <div className="mb-2">
        <label className="text-xs text-gray-500 block mb-0.5">Условия</label>
        {formulas.length === 0 ? (
          <p className="text-xs text-gray-400">Нет формул в библиотеке</p>
        ) : (
          <div className="space-y-0.5 max-h-40 overflow-auto border rounded p-1">
            {formulas.map((f) => (
              <label key={f.id} className="flex items-start gap-1.5 text-xs cursor-pointer hover:bg-gray-50 px-1 py-0.5 rounded">
                <input
                  type="checkbox"
                  checked={selectedConditions.has(f.id)}
                  onChange={() => toggleCondition(f.id)}
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

      {/* Target formula (phi) */}
      <div className="mb-2">
        <label className="text-xs text-gray-500 block mb-0.5">Целевая формула (φ)</label>
        <select
          value={phiId}
          onChange={(e) => setPhiId(e.target.value)}
          className="border rounded px-2 py-1 text-xs w-full"
        >
          <option value="">— выберите —</option>
          {formulas.map((f) => (
            <option key={f.id} value={f.id}>{f.name}</option>
          ))}
        </select>
      </div>

      {/* Action buttons */}
      <div className="flex gap-2 mb-2">
        <button
          onClick={handleCheck}
          disabled={selectedConditions.size === 0 || loading}
          className="text-xs bg-blue-600 text-white px-3 py-1 rounded disabled:opacity-50"
        >
          Проверить
        </button>
        <button
          onClick={handleForces}
          disabled={!phiId || loading}
          className="text-xs bg-purple-600 text-white px-3 py-1 rounded disabled:opacity-50"
        >
          Форсирует?
        </button>
      </div>

      {/* Check result */}
      {checkResult && (
        <div className="mb-2">
          <div className={`text-xs px-2 py-1 rounded mb-1 ${checkResult.ok ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
            {checkResult.ok ? "Все условия выполнены" : "Есть нарушения"}
          </div>
          <div className="space-y-0.5">
            {checkResult.conditions.map((c) => (
              <div key={c.formula_id} className="flex items-center gap-1.5 text-xs">
                <span className={`px-1.5 py-0.5 rounded text-[10px] ${RESULT_COLORS[c.result] ?? "bg-gray-100"}`}>
                  {RESULT_LABELS[c.result] ?? c.result}
                </span>
                <span className="font-medium">{c.formula_name}</span>
                <span className="text-gray-400 font-mono text-[10px] truncate">{c.formula_text}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Forces result */}
      {forcesResult && (
        <div className="mb-2">
          <div className="flex items-center gap-2 mb-1">
            <span className={`px-2 py-0.5 rounded text-xs font-semibold ${RESULT_COLORS[forcesResult.result] ?? "bg-gray-100"}`}>
              {RESULT_LABELS[forcesResult.result] ?? forcesResult.result}
            </span>
            <span className="text-xs text-gray-500">
              φ = {forcesResult.phi_name}
            </span>
          </div>
          <div className="space-y-0.5 mb-1">
            {forcesResult.conditions.map((c) => (
              <div key={c.formula_id} className="flex items-center gap-1.5 text-xs">
                <span className={`px-1.5 py-0.5 rounded text-[10px] ${RESULT_COLORS[c.result] ?? "bg-gray-100"}`}>
                  {RESULT_LABELS[c.result] ?? c.result}
                </span>
                <span className="font-medium">{c.formula_name}</span>
              </div>
            ))}
          </div>
          <button
            onClick={() => setShowExplanation(!showExplanation)}
            className="text-xs text-blue-600 hover:underline"
          >
            {showExplanation ? "Скрыть объяснение" : "Объяснение"}
          </button>
          {showExplanation && (
            <div className="mt-1 border rounded bg-gray-50 p-2 text-xs space-y-0.5">
              {forcesResult.explanation.map((line, i) => (
                <div key={i} className="text-gray-700">{line}</div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* History */}
      {history.length > 0 && (
        <div>
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="text-xs text-gray-500 hover:underline"
          >
            {showHistory ? "Скрыть историю" : `История (${history.length})`}
          </button>
          {showHistory && (
            <div className="mt-1 border rounded bg-gray-50 p-2 text-xs space-y-1 max-h-40 overflow-auto">
              {history.map((r) => (
                <div key={r.id} className="flex items-center gap-1.5">
                  <span className="text-gray-400 text-[10px]">{r.timestamp}</span>
                  <span className="font-medium">{r.type === "check" ? "check" : "forces"}</span>
                  <span className={`px-1 py-0.5 rounded text-[10px] ${RESULT_COLORS[r.result_summary] ?? "bg-gray-100"}`}>
                    {r.result_summary}
                  </span>
                  <span className="text-gray-400 truncate">
                    {r.context_name}
                    {r.phi_name ? ` → ${r.phi_name}` : ""}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

"use client";

import { ScenarioSpec } from "@/lib/types";

export function ScenarioBar({
  scenarios,
  scenario,
  setScenario,
  mode,
  setMode,
  derive,
  setDerive,
  onNewSession,
  onLoad,
  onRun,
}: {
  scenarios: ScenarioSpec[];
  scenario: string;
  setScenario: (s: string) => void;
  mode: string;
  setMode: (m: string) => void;
  derive: boolean;
  setDerive: (b: boolean) => void;
  onNewSession: () => void;
  onLoad: () => void;
  onRun: () => void;
}) {
  const current = scenarios.find((s) => s.name === scenario);

  return (
    <div className="flex items-center gap-2 border-b bg-white p-3">
      <button className="rounded-lg border px-3 py-1 text-sm hover:bg-zinc-50" onClick={onNewSession}>
        Новая сессия
      </button>

      <select className="rounded-lg border px-2 py-1 text-sm" value={scenario} onChange={(e) => setScenario(e.target.value)}>
        {scenarios.map((s) => (
          <option key={s.name} value={s.name}>{s.name}</option>
        ))}
      </select>

      <select className="rounded-lg border px-2 py-1 text-sm" value={mode} onChange={(e) => setMode(e.target.value)}>
        <option value="">(default)</option>
        {(current?.modes ?? []).map((m) => (
          <option key={m} value={m}>{m}</option>
        ))}
      </select>

      <label className="ml-2 flex items-center gap-2 text-sm">
        <input type="checkbox" checked={derive} onChange={(e) => setDerive(e.target.checked)} />
        вывод
      </label>

      <div className="flex-1" />

      <button className="rounded-lg border bg-blue-500 px-3 py-1 text-sm text-white hover:bg-blue-600" onClick={onLoad}>
        Загрузить
      </button>
      <button className="rounded-lg border bg-green-500 px-3 py-1 text-sm text-white hover:bg-green-600" onClick={onRun}>
        Запустить
      </button>
    </div>
  );
}

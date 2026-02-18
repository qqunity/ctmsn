"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import { WorkspaceList } from "@/components/WorkspaceList";
import { listScenarios, loadScenario, importWorkspace } from "@/lib/api";
import { ScenarioSpec } from "@/lib/types";

export default function WorkspacesPage() {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const [scenarios, setScenarios] = useState<ScenarioSpec[]>([]);
  const [scenario, setScenario] = useState("");
  const [mode, setMode] = useState("");
  const [wsName, setWsName] = useState("");
  const [creating, setCreating] = useState(false);
  const [key, setKey] = useState(0);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [user, loading, router]);

  useEffect(() => {
    listScenarios().then((s) => {
      setScenarios(s);
      if (s.length) setScenario(s[0].name);
    });
  }, []);

  const currentSpec = scenarios.find((s) => s.name === scenario);

  async function handleCreate() {
    setCreating(true);
    try {
      const res = await loadScenario({ scenario, mode: mode || null, name: wsName || null });
      router.push(`/workspace/${res.session_id}`);
    } catch {
      setCreating(false);
    }
  }

  async function handleImport(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const text = await file.text();
    try {
      const data = JSON.parse(text);
      const result = await importWorkspace(data);
      setKey((k) => k + 1);
    } catch {
      alert("Ошибка при импорте файла");
    }
    if (fileRef.current) fileRef.current.value = "";
  }

  if (loading || !user) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-3 flex items-center justify-between">
        <h1 className="text-lg font-bold">CTnSS</h1>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-600">
            {user.username} ({user.role === "teacher" ? "преподаватель" : "студент"})
          </span>
          {user.role === "teacher" && (
            <a href="/teacher" className="text-sm text-blue-600 hover:underline">
              Панель преподавателя
            </a>
          )}
          <button onClick={logout} className="text-sm text-red-600 hover:underline">
            Выйти
          </button>
        </div>
      </header>

      <main className="max-w-2xl mx-auto p-6 space-y-6">
        <section>
          <h2 className="text-lg font-semibold mb-3">Новое пространство</h2>
          <div className="space-y-2">
            <div className="flex gap-2 items-end">
              <div>
                <label className="block text-xs text-gray-500 mb-1">Сценарий</label>
                <select
                  value={scenario}
                  onChange={(e) => { setScenario(e.target.value); setMode(""); }}
                  className="border rounded px-3 py-2 text-sm"
                >
                  {scenarios.map((s) => (
                    <option key={s.name} value={s.name}>{s.name}</option>
                  ))}
                </select>
              </div>
              {currentSpec && currentSpec.modes.length > 0 && (
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Режим</label>
                  <select
                    value={mode}
                    onChange={(e) => setMode(e.target.value)}
                    className="border rounded px-3 py-2 text-sm"
                  >
                    <option value="">—</option>
                    {currentSpec.modes.map((m) => (
                      <option key={m} value={m}>{m}</option>
                    ))}
                  </select>
                </div>
              )}
              <div>
                <label className="block text-xs text-gray-500 mb-1">Имя (опционально)</label>
                <input
                  type="text"
                  value={wsName}
                  onChange={(e) => setWsName(e.target.value)}
                  placeholder="Автоматическое"
                  className="border rounded px-3 py-2 text-sm"
                />
              </div>
              <button
                onClick={handleCreate}
                disabled={creating}
                className="bg-blue-600 text-white rounded px-4 py-2 text-sm hover:bg-blue-700 disabled:opacity-50"
              >
                {creating ? "Создание..." : "Создать"}
              </button>
            </div>
          </div>
        </section>

        <section>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold">Мои пространства</h2>
            <label className="text-sm text-blue-600 hover:underline cursor-pointer">
              Импорт из файла
              <input
                ref={fileRef}
                type="file"
                accept=".json"
                className="hidden"
                onChange={handleImport}
              />
            </label>
          </div>
          <WorkspaceList key={key} />
        </section>
      </main>
    </div>
  );
}

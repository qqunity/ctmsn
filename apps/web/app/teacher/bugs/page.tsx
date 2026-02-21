"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import { listAllBugs, updateBugStatus, deleteBugReport, getBugScreenshotUrl } from "@/lib/api";
import { BugReportInfo } from "@/lib/types";

export default function TeacherBugsPage() {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const [bugs, setBugs] = useState<BugReportInfo[]>([]);
  const [filter, setFilter] = useState<"" | "open" | "closed">("");
  const [loadingBugs, setLoadingBugs] = useState(true);

  useEffect(() => {
    if (loading) return;
    if (!user) { router.replace("/login"); return; }
    if (user.role !== "teacher") { router.replace("/workspaces"); return; }
  }, [user, loading, router]);

  useEffect(() => {
    if (!user || user.role !== "teacher") return;
    fetchBugs();
  }, [user, filter]);

  async function fetchBugs() {
    setLoadingBugs(true);
    try {
      const data = await listAllBugs(filter || undefined);
      setBugs(data);
    } catch {
      // ignore
    } finally {
      setLoadingBugs(false);
    }
  }

  async function handleToggleStatus(bug: BugReportInfo) {
    const newStatus = bug.status === "open" ? "closed" : "open";
    try {
      const updated = await updateBugStatus(bug.id, newStatus);
      setBugs((prev) => prev.map((b) => (b.id === updated.id ? updated : b)));
    } catch {
      // ignore
    }
  }

  async function handleDelete(bugId: string) {
    if (!confirm("Удалить этот баг-репорт?")) return;
    try {
      await deleteBugReport(bugId);
      await fetchBugs();
    } catch {
      // ignore
    }
  }

  if (loading || !user || user.role !== "teacher") return null;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-lg font-bold">CTMSN — Баг-репорты</h1>
          <a href="/teacher" className="text-sm text-blue-600 hover:underline">
            Студенты
          </a>
          <a href="/workspaces" className="text-sm text-blue-600 hover:underline">
            Мои пространства
          </a>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-600">{user.username}</span>
          <button onClick={logout} className="text-sm text-red-600 hover:underline">
            Выйти
          </button>
        </div>
      </header>

      <main className="max-w-3xl mx-auto p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Баг-репорты</h2>
          <div className="flex gap-1">
            {(["", "open", "closed"] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-3 py-1 text-sm rounded ${
                  filter === f
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                }`}
              >
                {f === "" ? "Все" : f === "open" ? "Открытые" : "Закрытые"}
              </button>
            ))}
          </div>
        </div>

        {loadingBugs ? (
          <p className="text-sm text-gray-500">Загрузка...</p>
        ) : bugs.length === 0 ? (
          <p className="text-sm text-gray-500">Нет баг-репортов</p>
        ) : (
          <div className="space-y-3">
            {bugs.map((bug) => (
              <div key={bug.id} className="bg-white border rounded-lg p-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span
                        className={`inline-block px-2 py-0.5 text-xs rounded-full font-medium ${
                          bug.status === "open"
                            ? "bg-red-100 text-red-700"
                            : "bg-green-100 text-green-700"
                        }`}
                      >
                        {bug.status === "open" ? "Открыт" : "Закрыт"}
                      </span>
                      <h3 className="font-medium text-sm truncate">{bug.title}</h3>
                    </div>
                    <p className="text-sm text-gray-600 whitespace-pre-wrap mb-2">{bug.description}</p>
                    <div className="flex items-center gap-3 text-xs text-gray-400">
                      <span>Автор: {bug.author_username}</span>
                      {bug.workspace_name && <span>Пространство: {bug.workspace_name}</span>}
                      <span>{new Date(bug.created_at).toLocaleString()}</span>
                    </div>
                    {bug.has_screenshot && (
                      <div className="mt-2">
                        <img
                          src={getBugScreenshotUrl(bug.id)}
                          alt="Скриншот"
                          className="max-w-xs max-h-48 border rounded cursor-pointer"
                          onClick={() => window.open(getBugScreenshotUrl(bug.id), "_blank")}
                          onError={(e) => {
                            (e.target as HTMLImageElement).style.display = "none";
                          }}
                        />
                      </div>
                    )}
                  </div>
                  <div className="flex flex-col gap-1 shrink-0">
                    <button
                      onClick={() => handleToggleStatus(bug)}
                      className={`px-3 py-1 text-xs rounded ${
                        bug.status === "open"
                          ? "bg-green-600 text-white hover:bg-green-700"
                          : "bg-yellow-600 text-white hover:bg-yellow-700"
                      }`}
                    >
                      {bug.status === "open" ? "Закрыть" : "Открыть"}
                    </button>
                    <button
                      onClick={() => handleDelete(bug.id)}
                      className="px-3 py-1 text-xs rounded bg-red-600 text-white hover:bg-red-700"
                    >
                      Удалить
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

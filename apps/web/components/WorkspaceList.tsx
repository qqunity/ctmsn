"use client";

import { useEffect, useRef, useState } from "react";
import {
  listWorkspaces,
  renameWorkspace,
  deleteWorkspace,
  duplicateWorkspace,
  exportWorkspace,
  importWorkspace,
} from "@/lib/api";
import { WorkspaceInfo } from "@/lib/types";

export function WorkspaceList() {
  const [workspaces, setWorkspaces] = useState<WorkspaceInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editName, setEditName] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  async function reload() {
    const ws = await listWorkspaces();
    setWorkspaces(ws);
  }

  useEffect(() => {
    reload()
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  async function handleRename(id: string) {
    if (!editName.trim()) return;
    await renameWorkspace(id, editName.trim());
    setEditingId(null);
    await reload();
  }

  async function handleDuplicate(id: string) {
    const result = await duplicateWorkspace(id);
    await reload();
  }

  async function handleDelete(id: string) {
    if (!confirm("Удалить рабочее пространство?")) return;
    await deleteWorkspace(id);
    await reload();
  }

  async function handleExport(id: string) {
    const data = await exportWorkspace(id);
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `workspace-${id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  async function handleImport(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const text = await file.text();
    try {
      const data = JSON.parse(text);
      await importWorkspace(data);
      await reload();
    } catch {
      alert("Ошибка при импорте файла");
    }
    if (fileRef.current) fileRef.current.value = "";
  }

  if (loading) return <p className="text-gray-500">Загрузка...</p>;

  return (
    <div>
      <div className="flex justify-end mb-2">
        <label className="text-sm text-blue-600 hover:underline cursor-pointer">
          Импорт
          <input
            ref={fileRef}
            type="file"
            accept=".json"
            className="hidden"
            onChange={handleImport}
          />
        </label>
      </div>

      {workspaces.length === 0 ? (
        <p className="text-gray-500">Нет рабочих пространств. Создайте новое, загрузив сценарий.</p>
      ) : (
        <div className="space-y-2">
          {workspaces.map((w) => (
            <div
              key={w.id}
              className="border rounded p-3 hover:bg-gray-50 transition-colors"
            >
              <div className="flex justify-between items-center">
                <a href={`/workspace/${w.id}`} className="flex-1 min-w-0">
                  {editingId === w.id ? (
                    <div className="flex items-center gap-1" onClick={(e) => e.preventDefault()}>
                      <input
                        type="text"
                        value={editName}
                        onChange={(e) => setEditName(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter") handleRename(w.id);
                          if (e.key === "Escape") setEditingId(null);
                        }}
                        className="border rounded px-2 py-0.5 text-sm"
                        autoFocus
                        onClick={(e) => e.preventDefault()}
                      />
                      <button
                        onClick={(e) => { e.preventDefault(); handleRename(w.id); }}
                        className="text-xs text-green-600 hover:underline"
                      >
                        OK
                      </button>
                      <button
                        onClick={(e) => { e.preventDefault(); setEditingId(null); }}
                        className="text-xs text-gray-500 hover:underline"
                      >
                        Отмена
                      </button>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{w.name || w.scenario}</span>
                      {w.mode && <span className="text-sm text-gray-500">({w.mode})</span>}
                      {w.grade != null && (
                        <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold text-white ${
                          w.grade >= 8 ? "bg-green-500" : w.grade >= 5 ? "bg-yellow-500" : "bg-red-500"
                        }`}>
                          {w.grade}
                        </span>
                      )}
                    </div>
                  )}
                </a>
                <span className="text-xs text-gray-400 ml-2 shrink-0">
                  {new Date(w.updated_at).toLocaleString("ru")}
                </span>
              </div>
              <div className="flex gap-2 mt-1">
                <button
                  onClick={(e) => { e.stopPropagation(); setEditingId(w.id); setEditName(w.name || w.scenario); }}
                  className="text-xs text-blue-600 hover:underline"
                >
                  Переименовать
                </button>
                <button
                  onClick={() => handleDuplicate(w.id)}
                  className="text-xs text-blue-600 hover:underline"
                >
                  Дублировать
                </button>
                <button
                  onClick={() => handleExport(w.id)}
                  className="text-xs text-blue-600 hover:underline"
                >
                  Экспорт
                </button>
                <button
                  onClick={() => handleDelete(w.id)}
                  className="text-xs text-red-600 hover:underline"
                >
                  Удалить
                </button>
              </div>
              <p className="text-xs text-gray-400 mt-1">
                {w.scenario}{w.mode ? ` / ${w.mode}` : ""}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

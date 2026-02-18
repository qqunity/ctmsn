"use client";

import { useEffect, useState } from "react";
import { listWorkspaces } from "@/lib/api";
import { WorkspaceInfo } from "@/lib/types";

export function WorkspaceList() {
  const [workspaces, setWorkspaces] = useState<WorkspaceInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listWorkspaces()
      .then((ws) => setWorkspaces(ws))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-gray-500">Загрузка...</p>;

  if (workspaces.length === 0) {
    return <p className="text-gray-500">Нет рабочих пространств. Создайте новое, загрузив сценарий.</p>;
  }

  return (
    <div className="space-y-2">
      {workspaces.map((w) => (
        <a
          key={w.id}
          href={`/workspace/${w.id}`}
          className="block border rounded p-3 hover:bg-gray-50 transition-colors"
        >
          <div className="flex justify-between items-center">
            <div>
              <span className="font-medium">{w.scenario}</span>
              {w.mode && <span className="ml-2 text-sm text-gray-500">({w.mode})</span>}
            </div>
            <span className="text-xs text-gray-400">{new Date(w.created_at).toLocaleString("ru")}</span>
          </div>
          <p className="text-xs text-gray-400 mt-1">ID: {w.id}</p>
        </a>
      ))}
    </div>
  );
}

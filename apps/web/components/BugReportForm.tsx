"use client";

import { useRef, useState } from "react";
import { createBugReport, listMyBugs } from "@/lib/api";
import { BugReportInfo, WorkspaceInfo } from "@/lib/types";

type Props = {
  workspaces: WorkspaceInfo[];
  onClose: () => void;
  onCreated?: () => void;
};

export function BugReportForm({ workspaces, onClose, onCreated }: Props) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [workspaceId, setWorkspaceId] = useState("");
  const [screenshot, setScreenshot] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim() || !description.trim()) {
      setError("Заполните заголовок и описание");
      return;
    }

    setSubmitting(true);
    setError("");

    const fd = new FormData();
    fd.append("title", title.trim());
    fd.append("description", description.trim());
    if (workspaceId) fd.append("workspace_id", workspaceId);
    if (screenshot) fd.append("screenshot", screenshot);

    try {
      await createBugReport(fd);
      onCreated?.();
      onClose();
    } catch (err: any) {
      setError(err.message || "Ошибка при отправке");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-lg w-full max-w-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Сообщить о баге</h3>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="block text-sm text-gray-600 mb-1">Заголовок *</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full border rounded px-3 py-2 text-sm"
              placeholder="Кратко опишите проблему"
              maxLength={255}
            />
          </div>

          <div>
            <label className="block text-sm text-gray-600 mb-1">Описание *</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full border rounded px-3 py-2 text-sm"
              rows={4}
              placeholder="Подробное описание: что произошло, что ожидалось, шаги воспроизведения"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-600 mb-1">Пространство (опционально)</label>
            <select
              value={workspaceId}
              onChange={(e) => setWorkspaceId(e.target.value)}
              className="w-full border rounded px-3 py-2 text-sm"
            >
              <option value="">— Не привязано —</option>
              {workspaces.map((ws) => (
                <option key={ws.id} value={ws.id}>
                  {ws.name || ws.scenario}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm text-gray-600 mb-1">Скриншот (опционально)</label>
            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              onChange={(e) => setScreenshot(e.target.files?.[0] ?? null)}
              className="text-sm"
            />
            {screenshot && (
              <button
                type="button"
                onClick={() => {
                  setScreenshot(null);
                  if (fileRef.current) fileRef.current.value = "";
                }}
                className="text-xs text-red-500 ml-2"
              >
                Убрать
              </button>
            )}
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
            >
              Отмена
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="bg-red-600 text-white rounded px-4 py-2 text-sm hover:bg-red-700 disabled:opacity-50"
            >
              {submitting ? "Отправка..." : "Отправить"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

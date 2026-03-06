"use client";

import { useState } from "react";
import { setGrade, deleteGrade } from "@/lib/api";
import { GradeInfo } from "@/lib/types";

type Props = {
  workspaceId: string;
  initialGrade: GradeInfo | null;
};

export function GradePanel({ workspaceId, initialGrade }: Props) {
  const [gradeInfo, setGradeInfo] = useState<GradeInfo | null>(initialGrade);
  const [gradeValue, setGradeValue] = useState(initialGrade?.value ?? 5);
  const [editing, setEditing] = useState(false);

  async function handleSetGrade() {
    try {
      const g = await setGrade(workspaceId, gradeValue);
      setGradeInfo(g);
      setEditing(false);
    } catch {}
  }

  async function handleDeleteGrade() {
    try {
      await deleteGrade(workspaceId);
      setGradeInfo(null);
      setEditing(false);
    } catch {}
  }

  return (
    <div>
      <h3 className="text-sm font-semibold mb-2">Оценка</h3>
      {gradeInfo && !editing ? (
        <div className="flex items-center gap-3">
          <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold text-white ${
            gradeInfo.value >= 8 ? "bg-green-500" : gradeInfo.value >= 5 ? "bg-yellow-500" : "bg-red-500"
          }`}>
            {gradeInfo.value}
          </span>
          <span className="text-xs text-gray-500">
            {gradeInfo.teacher_username} &middot; {new Date(gradeInfo.updated_at).toLocaleString("ru")}
          </span>
          <button
            onClick={() => { setEditing(true); setGradeValue(gradeInfo.value); }}
            className="text-xs text-blue-600 hover:underline"
          >
            Изменить
          </button>
          <button
            onClick={handleDeleteGrade}
            className="text-xs text-red-600 hover:underline"
          >
            Снять
          </button>
        </div>
      ) : (
        <div className="flex items-center gap-2">
          <select
            value={gradeValue}
            onChange={(e) => setGradeValue(Number(e.target.value))}
            className="border rounded px-2 py-1 text-sm"
          >
            {Array.from({ length: 10 }, (_, i) => i + 1).map((v) => (
              <option key={v} value={v}>{v}</option>
            ))}
          </select>
          <button
            onClick={handleSetGrade}
            className="bg-blue-600 text-white rounded px-3 py-1 text-sm hover:bg-blue-700"
          >
            {gradeInfo ? "Сохранить" : "Поставить"}
          </button>
          {editing && (
            <button
              onClick={() => setEditing(false)}
              className="text-xs text-gray-500 hover:underline"
            >
              Отмена
            </button>
          )}
        </div>
      )}
    </div>
  );
}

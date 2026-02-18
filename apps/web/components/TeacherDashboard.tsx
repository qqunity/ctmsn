"use client";

import { useEffect, useState } from "react";
import { listStudents } from "@/lib/api";
import { StudentInfo } from "@/lib/types";

export function TeacherDashboard() {
  const [students, setStudents] = useState<StudentInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listStudents()
      .then(setStudents)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-gray-500">Загрузка...</p>;

  if (students.length === 0) {
    return <p className="text-gray-500">Нет зарегистрированных студентов.</p>;
  }

  return (
    <div className="space-y-2">
      {students.map((s) => (
        <a
          key={s.id}
          href={`/teacher/student/${s.id}`}
          className="block border rounded p-3 hover:bg-gray-50 transition-colors"
        >
          <div className="flex justify-between items-center">
            <span className="font-medium">{s.username}</span>
            <span className="text-sm text-gray-500">
              {s.workspace_count} {s.workspace_count === 1 ? "пространство" : "пространств"}
            </span>
          </div>
        </a>
      ))}
    </div>
  );
}

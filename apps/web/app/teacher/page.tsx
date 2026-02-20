"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import { TeacherDashboard } from "@/components/TeacherDashboard";

export default function TeacherPage() {
  const { user, loading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;
    if (!user) { router.replace("/login"); return; }
    if (user.role !== "teacher") { router.replace("/workspaces"); return; }
  }, [user, loading, router]);

  if (loading || !user || user.role !== "teacher") return null;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-lg font-bold">CTMSN — Преподаватель</h1>
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

      <main className="max-w-2xl mx-auto p-6">
        <h2 className="text-lg font-semibold mb-4">Студенты</h2>
        <TeacherDashboard />
      </main>
    </div>
  );
}

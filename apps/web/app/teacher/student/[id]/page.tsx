"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import { getStudentWorkspaces, getTeacherWorkspace, getTeacherComments, addTeacherComment } from "@/lib/api";
import { WorkspaceInfo, CommentInfo } from "@/lib/types";
import { GraphView } from "@/components/GraphView";

export default function StudentWorkspacesPage() {
  const { id: studentId } = useParams<{ id: string }>();
  const { user, loading: authLoading, logout } = useAuth();
  const router = useRouter();

  const [workspaces, setWorkspaces] = useState<WorkspaceInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedWs, setSelectedWs] = useState<string | null>(null);
  const [wsData, setWsData] = useState<any>(null);
  const [comments, setComments] = useState<CommentInfo[]>([]);
  const [commentText, setCommentText] = useState("");

  useEffect(() => {
    if (authLoading) return;
    if (!user) { router.replace("/login"); return; }
    if (user.role !== "teacher") { router.replace("/workspaces"); return; }
  }, [user, authLoading, router]);

  useEffect(() => {
    if (!studentId || !user) return;
    getStudentWorkspaces(studentId)
      .then(setWorkspaces)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [studentId, user]);

  async function openWorkspace(wsId: string) {
    setSelectedWs(wsId);
    try {
      const [data, cmts] = await Promise.all([
        getTeacherWorkspace(wsId),
        getTeacherComments(wsId),
      ]);
      setWsData(data);
      setComments(cmts);
    } catch {}
  }

  async function handleAddComment() {
    if (!selectedWs || !commentText.trim()) return;
    try {
      const c = await addTeacherComment(selectedWs, commentText.trim());
      setComments((prev) => [...prev, c]);
      setCommentText("");
    } catch {}
  }

  if (authLoading || !user || user.role !== "teacher") return null;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <a href="/teacher" className="text-sm text-blue-600 hover:underline">
            &larr; Назад
          </a>
          <h1 className="text-lg font-bold">Пространства студента</h1>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-600">{user.username}</span>
          <button onClick={logout} className="text-sm text-red-600 hover:underline">
            Выйти
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto p-6">
        {loading && <p className="text-gray-500">Загрузка...</p>}
        {!loading && workspaces.length === 0 && (
          <p className="text-gray-500">У студента нет пространств.</p>
        )}

        <div className="flex gap-6">
          <div className="w-64 shrink-0 space-y-2">
            {workspaces.map((w) => (
              <button
                key={w.id}
                onClick={() => openWorkspace(w.id)}
                className={`block w-full text-left border rounded p-2 text-sm transition-colors ${
                  selectedWs === w.id ? "bg-blue-50 border-blue-300" : "hover:bg-gray-50"
                }`}
              >
                <span className="font-medium">{w.scenario}</span>
                {w.mode && <span className="text-gray-500 ml-1">({w.mode})</span>}
                <p className="text-xs text-gray-400">{new Date(w.created_at).toLocaleString("ru")}</p>
              </button>
            ))}
          </div>

          {wsData && (
            <div className="flex-1 space-y-4">
              <div className="border rounded bg-white h-96">
                <GraphView graph={wsData.graph ?? null} onSelect={() => {}} />
              </div>

              <div className="border rounded bg-white p-4 space-y-3">
                <h3 className="font-semibold text-sm">Комментарии</h3>
                {comments.length === 0 && <p className="text-xs text-gray-400">Нет комментариев</p>}
                <div className="space-y-2 max-h-48 overflow-auto">
                  {comments.map((c) => (
                    <div key={c.id} className="border rounded p-2 text-sm">
                      <div className="flex justify-between text-xs text-gray-500 mb-1">
                        <span className="font-medium">{c.author_username}</span>
                        <span>{new Date(c.created_at).toLocaleString("ru")}</span>
                      </div>
                      <p>{c.text}</p>
                    </div>
                  ))}
                </div>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={commentText}
                    onChange={(e) => setCommentText(e.target.value)}
                    placeholder="Написать комментарий..."
                    className="flex-1 border rounded px-2 py-1 text-sm"
                  />
                  <button
                    onClick={handleAddComment}
                    disabled={!commentText.trim()}
                    className="bg-blue-600 text-white rounded px-3 py-1 text-sm hover:bg-blue-700 disabled:opacity-50"
                  >
                    Отправить
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

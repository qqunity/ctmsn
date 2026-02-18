"use client";

import { useEffect, useState } from "react";
import { getComments, addComment } from "@/lib/api";
import { CommentInfo } from "@/lib/types";

export function CommentPanel({ workspaceId }: { workspaceId: string }) {
  const [comments, setComments] = useState<CommentInfo[]>([]);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getComments(workspaceId).then(setComments).catch(() => {});
  }, [workspaceId]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!text.trim()) return;
    setLoading(true);
    try {
      const c = await addComment(workspaceId, text.trim());
      setComments((prev) => [...prev, c]);
      setText("");
    } catch {
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-3">
      <h3 className="font-semibold text-sm">Комментарии</h3>
      {comments.length === 0 && <p className="text-xs text-gray-400">Нет комментариев</p>}
      <div className="space-y-2 max-h-60 overflow-auto">
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
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Написать комментарий..."
          className="flex-1 border rounded px-2 py-1 text-sm"
        />
        <button
          type="submit"
          disabled={loading || !text.trim()}
          className="bg-blue-600 text-white rounded px-3 py-1 text-sm hover:bg-blue-700 disabled:opacity-50"
        >
          Отправить
        </button>
      </form>
    </div>
  );
}

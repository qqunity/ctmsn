"use client";

import { useState } from "react";
import { register } from "@/lib/api";
import { setTokens } from "@/lib/auth";
import { useAuth } from "./AuthProvider";

export function RegisterForm() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<"student" | "teacher">("student");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { refresh } = useAuth();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await register(username, password, role);
      setTokens(res.access_token, res.refresh_token);
      await refresh();
    } catch (err: any) {
      setError(err.message || "Ошибка регистрации");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 w-full max-w-sm">
      <h2 className="text-xl font-bold">Регистрация</h2>
      {error && <p className="text-red-600 text-sm">{error}</p>}
      <input
        type="text"
        placeholder="Имя пользователя"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        className="block w-full border rounded px-3 py-2"
        required
      />
      <input
        type="password"
        placeholder="Пароль"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="block w-full border rounded px-3 py-2"
        required
      />
      <div>
        <label className="block text-sm font-medium mb-1">Роль</label>
        <select
          value={role}
          onChange={(e) => setRole(e.target.value as "student" | "teacher")}
          className="block w-full border rounded px-3 py-2"
        >
          <option value="student">Студент</option>
          <option value="teacher">Преподаватель</option>
        </select>
      </div>
      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 text-white rounded px-4 py-2 hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? "Регистрация..." : "Зарегистрироваться"}
      </button>
      <p className="text-sm text-gray-600">
        Уже есть аккаунт?{" "}
        <a href="/login" className="text-blue-600 hover:underline">
          Войти
        </a>
      </p>
    </form>
  );
}

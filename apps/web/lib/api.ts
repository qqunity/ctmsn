import {
  LoadResponse,
  ScenarioSpec,
  AddConceptRequest,
  AddPredicateRequest,
  AddFactRequest,
  NetworkEditResponse,
  TokenResponse,
  UserInfo,
  WorkspaceInfo,
  CommentInfo,
  StudentInfo,
} from "./types";
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from "./auth";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

async function authFetch(url: string, init?: RequestInit): Promise<Response> {
  const token = getAccessToken();
  const headers: Record<string, string> = {
    ...(init?.headers as Record<string, string> ?? {}),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  let res = await fetch(url, { ...init, headers });

  if (res.status === 401 || res.status === 403) {
    const refreshToken = getRefreshToken();
    if (refreshToken) {
      const refreshRes = await fetch(`${API_BASE}/api/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
      if (refreshRes.ok) {
        const data: TokenResponse = await refreshRes.json();
        setTokens(data.access_token, data.refresh_token);
        headers["Authorization"] = `Bearer ${data.access_token}`;
        res = await fetch(url, { ...init, headers });
      } else {
        clearTokens();
      }
    }
  }

  return res;
}

async function ensureOk(res: Response): Promise<any> {
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || data.error || "Request failed");
  }
  return data;
}

// Auth
export async function login(username: string, password: string): Promise<TokenResponse> {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  return ensureOk(res);
}

export async function register(username: string, password: string, role: string): Promise<TokenResponse> {
  const res = await fetch(`${API_BASE}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password, role }),
  });
  return ensureOk(res);
}

export async function getMe(): Promise<UserInfo> {
  const res = await authFetch(`${API_BASE}/api/auth/me`);
  return ensureOk(res);
}

// Scenarios (public)
export async function listScenarios(): Promise<ScenarioSpec[]> {
  const r = await fetch(`${API_BASE}/api/scenarios`);
  const j = await r.json();
  return j.scenarios as ScenarioSpec[];
}

// Session / Workspace
export async function loadScenario(req: {
  scenario: string;
  mode?: string | null;
  derive?: boolean;
}): Promise<LoadResponse> {
  const r = await authFetch(`${API_BASE}/api/session/load`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...req, derive: req.derive ?? true }),
  });
  return (await r.json()) as LoadResponse;
}

export async function runScenario(req: { session_id: string; derive?: boolean }): Promise<LoadResponse> {
  const r = await authFetch(`${API_BASE}/api/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...req, derive: req.derive ?? true }),
  });
  return (await r.json()) as LoadResponse;
}

export async function addConcept(req: AddConceptRequest): Promise<NetworkEditResponse> {
  const r = await authFetch(`${API_BASE}/api/session/add_concept`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  return (await r.json()) as NetworkEditResponse;
}

export async function addPredicate(req: AddPredicateRequest): Promise<NetworkEditResponse> {
  const r = await authFetch(`${API_BASE}/api/session/add_predicate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  return (await r.json()) as NetworkEditResponse;
}

export async function addFact(req: AddFactRequest): Promise<NetworkEditResponse> {
  const r = await authFetch(`${API_BASE}/api/session/add_fact`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  return (await r.json()) as NetworkEditResponse;
}

// Workspaces
export async function listWorkspaces(): Promise<WorkspaceInfo[]> {
  const r = await authFetch(`${API_BASE}/api/workspaces`);
  const j = await r.json();
  return j.workspaces as WorkspaceInfo[];
}

// Comments
export async function getComments(workspaceId: string): Promise<CommentInfo[]> {
  const r = await authFetch(`${API_BASE}/api/workspaces/${workspaceId}/comments`);
  const j = await r.json();
  return j.comments as CommentInfo[];
}

export async function addComment(workspaceId: string, text: string): Promise<CommentInfo> {
  const r = await authFetch(`${API_BASE}/api/workspaces/${workspaceId}/comments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  return ensureOk(r);
}

// Teacher
export async function listStudents(): Promise<StudentInfo[]> {
  const r = await authFetch(`${API_BASE}/api/teacher/students`);
  return ensureOk(r);
}

export async function getStudentWorkspaces(studentId: string): Promise<WorkspaceInfo[]> {
  const r = await authFetch(`${API_BASE}/api/teacher/students/${studentId}/workspaces`);
  return ensureOk(r);
}

export async function getTeacherWorkspace(workspaceId: string): Promise<any> {
  const r = await authFetch(`${API_BASE}/api/teacher/workspaces/${workspaceId}`);
  return ensureOk(r);
}

export async function getTeacherComments(workspaceId: string): Promise<CommentInfo[]> {
  const r = await authFetch(`${API_BASE}/api/teacher/workspaces/${workspaceId}/comments`);
  return ensureOk(r);
}

export async function addTeacherComment(workspaceId: string, text: string): Promise<CommentInfo> {
  const r = await authFetch(`${API_BASE}/api/teacher/workspaces/${workspaceId}/comments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  return ensureOk(r);
}

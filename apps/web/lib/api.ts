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
  GradeInfo,
  FormulaNode,
  FormulaInfo,
  UserVariableInfo,
  NamedContextInfo,
  ContextCompareResult,
  ContextHighlights,
  ForcingCheckResult,
  ForcingForcesResult,
  CascadeInfo,
  HistoryStatus,
  UndoRedoResponse,
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

export async function register(username: string, password: string): Promise<TokenResponse> {
  const res = await fetch(`${API_BASE}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
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
  name?: string | null;
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

export async function setVariable(sessionId: string, variable: string, value: string): Promise<LoadResponse> {
  const r = await authFetch(`${API_BASE}/api/session/set_variable`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, variable, value }),
  });
  return ensureOk(r);
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

export async function renameWorkspace(id: string, name: string): Promise<{ ok: boolean; id: string; name: string }> {
  const r = await authFetch(`${API_BASE}/api/workspaces/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  return ensureOk(r);
}

export async function deleteWorkspace(id: string): Promise<{ ok: boolean }> {
  const r = await authFetch(`${API_BASE}/api/workspaces/${id}`, {
    method: "DELETE",
  });
  return ensureOk(r);
}

export async function duplicateWorkspace(id: string): Promise<{ id: string; name: string }> {
  const r = await authFetch(`${API_BASE}/api/workspaces/${id}/duplicate`, {
    method: "POST",
  });
  return ensureOk(r);
}

export async function exportWorkspace(id: string): Promise<any> {
  const r = await authFetch(`${API_BASE}/api/workspaces/${id}/export`);
  return ensureOk(r);
}

export async function importWorkspace(data: any): Promise<{ id: string; name: string }> {
  const r = await authFetch(`${API_BASE}/api/workspaces/import`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ data }),
  });
  return ensureOk(r);
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

export async function setGrade(workspaceId: string, value: number): Promise<GradeInfo> {
  const r = await authFetch(`${API_BASE}/api/teacher/workspaces/${workspaceId}/grade`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ value }),
  });
  return ensureOk(r);
}

export async function deleteGrade(workspaceId: string): Promise<{ ok: boolean }> {
  const r = await authFetch(`${API_BASE}/api/teacher/workspaces/${workspaceId}/grade`, {
    method: "DELETE",
  });
  return ensureOk(r);
}

// ─── Formula CRUD ────────────────────────────────────────────

export async function listFormulas(workspaceId: string): Promise<FormulaInfo[]> {
  const r = await authFetch(`${API_BASE}/api/workspaces/${workspaceId}/formulas`);
  const j = await r.json();
  return j.formulas as FormulaInfo[];
}

export async function createFormula(workspaceId: string, name: string, formula: FormulaNode): Promise<FormulaInfo> {
  const r = await authFetch(`${API_BASE}/api/workspaces/${workspaceId}/formulas`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, formula }),
  });
  return ensureOk(r);
}

export async function updateFormula(workspaceId: string, formulaId: string, data: { name?: string; formula?: FormulaNode }): Promise<FormulaInfo> {
  const r = await authFetch(`${API_BASE}/api/workspaces/${workspaceId}/formulas/${formulaId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return ensureOk(r);
}

export async function deleteFormula(workspaceId: string, formulaId: string): Promise<{ ok: boolean }> {
  const r = await authFetch(`${API_BASE}/api/workspaces/${workspaceId}/formulas/${formulaId}`, {
    method: "DELETE",
  });
  return ensureOk(r);
}

export async function evaluateFormula(workspaceId: string, formulaId: string, contextId?: string): Promise<{ result: string }> {
  const r = await authFetch(`${API_BASE}/api/workspaces/${workspaceId}/formulas/${formulaId}/evaluate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ context_id: contextId ?? null }),
  });
  return ensureOk(r);
}

// ─── Variable CRUD ───────────────────────────────────────────

export async function listAllVariables(workspaceId: string): Promise<UserVariableInfo[]> {
  const r = await authFetch(`${API_BASE}/api/workspaces/${workspaceId}/variables`);
  const j = await r.json();
  return j.variables as UserVariableInfo[];
}

export async function createVariable(workspaceId: string, data: { name: string; type_tag?: string; domain_type: string; domain: Record<string, any> }): Promise<UserVariableInfo> {
  const r = await authFetch(`${API_BASE}/api/workspaces/${workspaceId}/variables`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return ensureOk(r);
}

export async function updateVariable(workspaceId: string, varId: string, data: { name?: string; type_tag?: string; domain_type?: string; domain?: Record<string, any> }): Promise<UserVariableInfo> {
  const r = await authFetch(`${API_BASE}/api/workspaces/${workspaceId}/variables/${varId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return ensureOk(r);
}

export async function deleteVariable(workspaceId: string, varId: string): Promise<{ ok: boolean }> {
  const r = await authFetch(`${API_BASE}/api/workspaces/${workspaceId}/variables/${varId}`, {
    method: "DELETE",
  });
  return ensureOk(r);
}

// ─── Context CRUD ────────────────────────────────────────────

export async function listContexts(workspaceId: string): Promise<NamedContextInfo[]> {
  const r = await authFetch(`${API_BASE}/api/workspaces/${workspaceId}/contexts`);
  const j = await r.json();
  return j.contexts as NamedContextInfo[];
}

export async function createContext(workspaceId: string, name: string, cloneFrom?: string): Promise<NamedContextInfo> {
  const r = await authFetch(`${API_BASE}/api/workspaces/${workspaceId}/contexts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, clone_from: cloneFrom ?? null }),
  });
  return ensureOk(r);
}

export async function updateContext(workspaceId: string, contextId: string, data: { name?: string; context?: Record<string, any> }): Promise<NamedContextInfo> {
  const r = await authFetch(`${API_BASE}/api/workspaces/${workspaceId}/contexts/${contextId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return ensureOk(r);
}

export async function deleteContext(workspaceId: string, contextId: string): Promise<{ ok: boolean }> {
  const r = await authFetch(`${API_BASE}/api/workspaces/${workspaceId}/contexts/${contextId}`, {
    method: "DELETE",
  });
  return ensureOk(r);
}

export async function activateContext(workspaceId: string, contextId: string): Promise<NamedContextInfo> {
  const r = await authFetch(`${API_BASE}/api/workspaces/${workspaceId}/contexts/${contextId}/activate`, {
    method: "POST",
  });
  return ensureOk(r);
}

export async function setContextVariable(workspaceId: string, contextId: string, variable: string, value: any): Promise<NamedContextInfo> {
  const r = await authFetch(`${API_BASE}/api/workspaces/${workspaceId}/contexts/${contextId}/set_variable`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ variable, value }),
  });
  return ensureOk(r);
}

export async function compareContexts(workspaceId: string, contextIds: string[]): Promise<ContextCompareResult> {
  const r = await authFetch(`${API_BASE}/api/workspaces/${workspaceId}/contexts/compare`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ context_ids: contextIds }),
  });
  return ensureOk(r);
}

export async function getContextHighlights(workspaceId: string, contextId: string): Promise<ContextHighlights> {
  const r = await authFetch(`${API_BASE}/api/workspaces/${workspaceId}/contexts/${contextId}/highlights`);
  return ensureOk(r);
}

// ─── Forcing ─────────────────────────────────────────────────

export async function runForcingCheck(
  workspaceId: string,
  req: { context_id?: string | null; condition_ids: string[] },
): Promise<ForcingCheckResult> {
  const r = await authFetch(`${API_BASE}/api/workspaces/${workspaceId}/forcing/check`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  return ensureOk(r);
}

export async function runForcingForces(
  workspaceId: string,
  req: { context_id?: string | null; condition_ids: string[]; phi_id: string },
): Promise<ForcingForcesResult> {
  const r = await authFetch(`${API_BASE}/api/workspaces/${workspaceId}/forcing/forces`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  return ensureOk(r);
}

// ─── Cascade / Delete / Edit ─────────────────────────────────

export async function getCascadeInfo(sessionId: string, type: "concept" | "predicate", id: string): Promise<CascadeInfo> {
  const r = await authFetch(`${API_BASE}/api/session/${sessionId}/cascade/${type}/${encodeURIComponent(id)}`);
  return ensureOk(r);
}

export async function removeConcept(sessionId: string, conceptId: string): Promise<NetworkEditResponse> {
  const r = await authFetch(`${API_BASE}/api/session/remove_concept`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, concept_id: conceptId }),
  });
  return (await r.json()) as NetworkEditResponse;
}

export async function removePredicate(sessionId: string, predicateName: string): Promise<NetworkEditResponse> {
  const r = await authFetch(`${API_BASE}/api/session/remove_predicate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, predicate_name: predicateName }),
  });
  return (await r.json()) as NetworkEditResponse;
}

export async function removeFact(sessionId: string, predicate: string, args: string[]): Promise<NetworkEditResponse> {
  const r = await authFetch(`${API_BASE}/api/session/remove_fact`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, predicate, args }),
  });
  return (await r.json()) as NetworkEditResponse;
}

export async function editConcept(sessionId: string, conceptId: string, data: { label?: string; tags?: string[] }): Promise<NetworkEditResponse> {
  const r = await authFetch(`${API_BASE}/api/session/edit_concept`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, concept_id: conceptId, ...data }),
  });
  return (await r.json()) as NetworkEditResponse;
}

export async function editPredicate(sessionId: string, predicateName: string, data: { arity?: number }): Promise<NetworkEditResponse> {
  const r = await authFetch(`${API_BASE}/api/session/edit_predicate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, predicate_name: predicateName, ...data }),
  });
  return (await r.json()) as NetworkEditResponse;
}

// ─── Undo / Redo ─────────────────────────────────────────────

export async function undoNetwork(sessionId: string): Promise<UndoRedoResponse> {
  const r = await authFetch(`${API_BASE}/api/session/${sessionId}/undo`, { method: "POST" });
  return (await r.json()) as UndoRedoResponse;
}

export async function redoNetwork(sessionId: string): Promise<UndoRedoResponse> {
  const r = await authFetch(`${API_BASE}/api/session/${sessionId}/redo`, { method: "POST" });
  return (await r.json()) as UndoRedoResponse;
}

export async function getHistoryStatus(sessionId: string): Promise<HistoryStatus> {
  const r = await authFetch(`${API_BASE}/api/session/${sessionId}/history`);
  return ensureOk(r);
}

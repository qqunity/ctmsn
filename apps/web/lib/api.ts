import { LoadResponse, ScenarioSpec, AddConceptRequest, AddPredicateRequest, AddFactRequest, NetworkEditResponse } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

export async function listScenarios(): Promise<ScenarioSpec[]> {
  const r = await fetch(`${API_BASE}/api/scenarios`);
  const j = await r.json();
  return j.scenarios as ScenarioSpec[];
}

export async function newSession(): Promise<string> {
  const r = await fetch(`${API_BASE}/api/session/new`, { method: "POST" });
  const j = await r.json();
  return j.session_id as string;
}

export async function loadScenario(req: {
  session_id: string;
  scenario: string;
  mode?: string | null;
  derive?: boolean;
}): Promise<LoadResponse> {
  const r = await fetch(`${API_BASE}/api/session/load`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...req, derive: req.derive ?? true }),
  });
  return (await r.json()) as LoadResponse;
}

export async function runScenario(req: { session_id: string; derive?: boolean }): Promise<LoadResponse> {
  const r = await fetch(`${API_BASE}/api/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...req, derive: req.derive ?? true }),
  });
  return (await r.json()) as LoadResponse;
}

export async function addConcept(req: AddConceptRequest): Promise<NetworkEditResponse> {
  const r = await fetch(`${API_BASE}/api/session/add_concept`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  return (await r.json()) as NetworkEditResponse;
}

export async function addPredicate(req: AddPredicateRequest): Promise<NetworkEditResponse> {
  const r = await fetch(`${API_BASE}/api/session/add_predicate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  return (await r.json()) as NetworkEditResponse;
}

export async function addFact(req: AddFactRequest): Promise<NetworkEditResponse> {
  const r = await fetch(`${API_BASE}/api/session/add_fact`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  return (await r.json()) as NetworkEditResponse;
}

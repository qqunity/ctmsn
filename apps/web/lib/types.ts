export type ScenarioSpec = { name: string; modes: string[] };

export type GraphNode = { id: string; label: string; tags?: string[] };
export type GraphEdge = { id: string; label: string; source: string; target: string; kind: "edge" | "derived" };

export type Equation =
  | { kind: "comp2"; left: string; right: string; result: string }
  | { kind: "compN"; chain: string; result: string };

export type Predicate = { name: string; arity: number };

export type GraphPayload = {
  nodes: GraphNode[];
  edges: GraphEdge[];
  equations: Equation[];
  traces: { comp2: any[]; compN: any[] };
  predicates: Predicate[];
};

export type VariableInfo = {
  name: string;
  type_tag: string | null;
  domain_type: "enum" | "range" | "predicate";
  values?: string[];
  min?: number;
  max?: number;
};

export type LoadResponse = {
  session_id: string;
  name?: string;
  scenario: string;
  mode: string | null;
  graph: GraphPayload;
  derivation: any;
  check: string | null;
  forces: string | null;
  force: string | null;
  variables?: VariableInfo[] | null;
  context?: Record<string, any>;
};

export type AddConceptRequest = {
  session_id: string;
  id: string;
  label: string;
  tags?: string[];
};

export type AddPredicateRequest = {
  session_id: string;
  name: string;
  arity: number;
};

export type AddFactRequest = {
  session_id: string;
  predicate: string;
  args: string[];
};

export type NetworkEditResponse = {
  ok?: boolean;
  error?: string;
  graph?: GraphPayload;
};

export type UserInfo = {
  id: string;
  username: string;
  role: "student" | "teacher";
};

export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  role: string;
};

export type WorkspaceInfo = {
  id: string;
  name: string;
  scenario: string;
  mode: string | null;
  created_at: string;
  updated_at: string;
  grade?: number | null;
};

export type GradeInfo = {
  value: number;
  teacher_username: string;
  updated_at: string;
};

export type CommentInfo = {
  id: string;
  author_id: string;
  author_username: string;
  text: string;
  created_at: string;
};

export type StudentInfo = {
  id: string;
  username: string;
  workspace_count: number;
};

// ─── Formula Editor Types ────────────────────────────────────

export type TermRef =
  | { kind: "concept"; id: string }
  | { kind: "variable"; name: string }
  | { kind: "literal"; value: string | number | boolean };

export type FormulaNode =
  | { type: "FactAtom"; predicate: string; args: TermRef[] }
  | { type: "EqAtom"; left: TermRef; right: TermRef }
  | { type: "Not"; inner: FormulaNode }
  | { type: "And"; items: FormulaNode[] }
  | { type: "Or"; items: FormulaNode[] }
  | { type: "Implies"; left: FormulaNode; right: FormulaNode };

export type FormulaInfo = {
  id: string;
  name: string;
  formula: FormulaNode;
  text: string;
  created_at: string | null;
  updated_at: string | null;
};

// ─── Variable/Domain Editor Types ────────────────────────────

export type UserVariableInfo = {
  id?: string;
  name: string;
  type_tag: string | null;
  domain_type: "enum" | "range" | "predicate";
  domain?: Record<string, any>;
  values?: string[];
  min?: number;
  max?: number;
  origin: "scenario" | "user";
  created_at?: string | null;
};

// ─── Context Editor Types ────────────────────────────────────

export type NamedContextInfo = {
  id: string;
  name: string;
  context: Record<string, any>;
  is_active: boolean;
  is_complete: boolean;
  total_vars: number;
  assigned_vars: number;
  created_at: string | null;
  updated_at: string | null;
};

export type ContextCompareResult = {
  contexts: NamedContextInfo[];
  diff: Record<string, any[]>;
};

export type ContextHighlights = {
  nodes: string[];
  edges: string[];
};

// ─── Forcing Panel Types ────────────────────────────────────

export type ConditionResultItem = {
  formula_id: string;
  formula_name: string;
  formula_text: string;
  result: "true" | "false" | "unknown";
};

export type ForcingCheckResult = {
  ok: boolean;
  conditions: ConditionResultItem[];
};

export type ForcingForcesResult = {
  result: "true" | "false" | "unknown";
  phi_name: string;
  phi_text: string;
  phi_result: string;
  conditions_ok: boolean;
  conditions: ConditionResultItem[];
  explanation: string[];
};

export type CascadeInfo = {
  count: number;
  affected_facts: Array<{ predicate: string; args: string[] }>;
};

export type HistoryStatus = {
  can_undo: boolean;
  can_redo: boolean;
  undo_count: number;
  redo_count: number;
};

export type UndoRedoResponse = {
  ok: boolean;
  error?: string;
  graph?: GraphPayload;
  can_undo: boolean;
  can_redo: boolean;
};

export type BugReportInfo = {
  id: string;
  author_username: string;
  workspace_id: string | null;
  workspace_name: string | null;
  title: string;
  description: string;
  has_screenshot: boolean;
  status: "open" | "closed";
  created_at: string;
};

export type ForcingRunRecord = {
  id: string;
  timestamp: string;
  type: "check" | "forces";
  context_name: string;
  condition_names: string[];
  phi_name: string | null;
  result_summary: string;
};

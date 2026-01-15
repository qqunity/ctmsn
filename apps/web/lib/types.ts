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

export type LoadResponse = {
  session_id: string;
  scenario: string;
  mode: string | null;
  graph: GraphPayload;
  derivation: any;
  check: string | null;
  forces: string | null;
  force: string | null;
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

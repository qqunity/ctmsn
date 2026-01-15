export type ScenarioSpec = { name: string; modes: string[] };

export type GraphNode = { id: string; label: string };
export type GraphEdge = { id: string; label: string; source: string; target: string; kind: "edge" | "derived" };

export type Equation =
  | { kind: "comp2"; left: string; right: string; result: string }
  | { kind: "compN"; chain: string; result: string };

export type GraphPayload = {
  nodes: GraphNode[];
  edges: GraphEdge[];
  equations: Equation[];
  traces: { comp2: any[]; compN: any[] };
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

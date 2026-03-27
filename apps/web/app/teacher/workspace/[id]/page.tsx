"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import { runScenario, getTeacherWorkspace, exportWorkspace } from "@/lib/api";
import { LoadResponse, Equation, ContextHighlights, FormulaInfo, NamedContextInfo } from "@/lib/types";
import { GraphView, GraphViewHandle } from "@/components/GraphView";
import { StatusPanel } from "@/components/StatusPanel";
import { EquationsPanel } from "@/components/EquationsPanel";
import { DetailsPanel } from "@/components/DetailsPanel";
import { CommentPanel } from "@/components/CommentPanel";
import { VariableEditorPanel } from "@/components/VariableEditorPanel";
import { ContextEditorPanel } from "@/components/ContextEditorPanel";
import { FormulaEditorPanel } from "@/components/FormulaEditorPanel";
import { ForcingPanel } from "@/components/ForcingPanel";
import { GraphLegend } from "@/components/GraphLegend";
import { LayoutSelector } from "@/components/LayoutSelector";
import { NetworkStatsPanel } from "@/components/NetworkStatsPanel";
import { GradePanel } from "@/components/GradePanel";
import { ContradictionsBanner } from "@/components/ContradictionsBanner";
import { GradeInfo } from "@/lib/types";

export default function TeacherWorkspacePage() {
  const { id } = useParams<{ id: string }>();
  const { user, loading: authLoading, logout } = useAuth();
  const router = useRouter();

  const [sessionId] = useState<string>(id);
  const [data, setData] = useState<LoadResponse | null>(null);
  const [selected, setSelected] = useState<any>(null);
  const [wsName, setWsName] = useState<string>("");
  const [gradeInfo, setGradeInfo] = useState<GradeInfo | null>(null);

  const [highlights, setHighlights] = useState<ContextHighlights | null>(null);
  const [activeTermPickerId, setActiveTermPickerId] = useState<string | null>(null);
  const [sharedFormulas, setSharedFormulas] = useState<FormulaInfo[]>([]);
  const [sharedContexts, setSharedContexts] = useState<NamedContextInfo[]>([]);
  const [graphLayout, setGraphLayout] = useState("cose");
  const [eqHighlights, setEqHighlights] = useState<ContextHighlights | null>(null);
  const graphRef = useRef<GraphViewHandle>(null);

  useEffect(() => {
    if (authLoading) return;
    if (!user) { router.replace("/login"); return; }
    if (user.role !== "teacher") { router.replace("/workspaces"); return; }
  }, [user, authLoading, router]);

  useEffect(() => {
    if (!id || !user) return;
    Promise.all([
      runScenario({ session_id: id, derive: true }),
      getTeacherWorkspace(id),
    ]).then(([payload, wsData]) => {
      setData(payload);
      setWsName(payload.name ?? "");
      setGradeInfo(wsData.grade ?? null);
    }).catch(() => {});
  }, [id, user]);

  const handleVariableUpdate = useCallback((resp: LoadResponse) => {
    setData(resp);
  }, []);

  const handleContextActivate = useCallback(() => {
    if (sessionId) {
      runScenario({ session_id: sessionId, derive: true })
        .then((payload) => setData(payload))
        .catch(() => {});
    }
  }, [sessionId]);

  const handleGraphSelect = useCallback((x: any) => {
    setSelected(x);
    setEqHighlights(null);
  }, []);

  const handleFormulasChange = useCallback((formulas: FormulaInfo[]) => {
    setSharedFormulas(formulas);
  }, []);

  const handleContextsChange = useCallback((contexts: NamedContextInfo[]) => {
    setSharedContexts(contexts);
  }, []);

  function pickEq(eq: Equation) {
    setSelected(eq);

    if (!data?.graph) {
      setEqHighlights(null);
      return;
    }

    const nodeIds = new Set<string>();
    const edgeIds = new Set<string>();
    const edges = data.graph.edges;

    if (eq.kind === "comp2") {
      for (const e of edges) {
        if (e.label === eq.left || e.label === eq.right || e.label === eq.result) {
          edgeIds.add(e.id);
          nodeIds.add(e.source);
          nodeIds.add(e.target);
        }
      }
      if (data.graph.traces?.comp2) {
        for (const t of data.graph.traces.comp2) {
          if (t.result === eq.result && t.left === eq.left && t.right === eq.right) {
            if (t.mid) nodeIds.add(t.mid);
          }
        }
      }
    } else {
      const labels = eq.chain.split(";").map((s: string) => s.trim());
      labels.push(eq.result);
      for (const e of edges) {
        if (labels.includes(e.label)) {
          edgeIds.add(e.id);
          nodeIds.add(e.source);
          nodeIds.add(e.target);
        }
      }
    }

    setEqHighlights({ nodes: Array.from(nodeIds), edges: Array.from(edgeIds) });
  }

  async function handleExportJson() {
    if (!sessionId) return;
    const data = await exportWorkspace(sessionId);
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${wsName || "workspace"}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function handleExportPng() {
    const dataUrl = graphRef.current?.exportPng();
    if (!dataUrl) return;
    const a = document.createElement("a");
    a.href = dataUrl;
    a.download = `${wsName || "workspace"}.png`;
    a.click();
  }

  if (authLoading || !user || user.role !== "teacher") return null;

  return (
    <div className="flex h-screen flex-col">
      <div className="flex items-center gap-2 border-b bg-white px-3 py-2">
        <a href="/teacher" className="text-sm text-blue-600 hover:underline mr-2">
          &larr; Назад
        </a>
        <span className="text-sm font-medium">
          {wsName || "Без имени"}
        </span>
        <span className="ml-2 px-2 py-0.5 rounded text-xs bg-amber-100 text-amber-700 font-medium">
          Только просмотр
        </span>
        <div className="flex items-center gap-1 ml-4">
          <LayoutSelector value={graphLayout} onChange={setGraphLayout} />
        </div>
        <div className="flex items-center gap-1 ml-2">
          <button
            onClick={handleExportJson}
            className="rounded px-2 py-1 text-xs hover:bg-gray-100"
          >
            &#x1F4E5; JSON
          </button>
          <button
            onClick={handleExportPng}
            className="rounded px-2 py-1 text-xs hover:bg-gray-100"
          >
            &#x1F4F7; PNG
          </button>
        </div>
        <div className="flex-1" />
        <span className="text-sm text-gray-500">{user.username}</span>
        <button onClick={logout} className="text-sm text-red-600 hover:underline">
          Выйти
        </button>
      </div>

      {data?.contradictions && data.contradictions.length > 0 && (
        <div className="px-3 pt-2">
          <ContradictionsBanner items={data.contradictions} />
        </div>
      )}

      <div className="flex flex-1 overflow-hidden overflow-x-hidden">
        <div className="flex-1 relative">
          <GraphView
            ref={graphRef}
            graph={data?.graph ?? null}
            onSelect={handleGraphSelect}
            highlights={highlights}
            layout={graphLayout}
            equationHighlights={eqHighlights}
          />
          <GraphLegend />
        </div>

        <div className="w-[460px] min-w-[300px] shrink overflow-auto border-l bg-white p-4">
          <div className="space-y-4">
            <NetworkStatsPanel graph={data?.graph ?? null} />
            <StatusPanel data={data} />
            <GradePanel workspaceId={sessionId} initialGrade={gradeInfo} />
            {data?.variables && data.variables.length > 0 && (
              <VariableEditorPanel
                variables={data.variables}
                context={data.context ?? {}}
                sessionId={sessionId}
                graph={data?.graph ?? null}
                onUpdate={handleVariableUpdate}
                readOnly
              />
            )}
            {sessionId && (
              <ContextEditorPanel
                sessionId={sessionId}
                variables={data?.variables ?? []}
                onActivate={handleContextActivate}
                onHighlightsChange={setHighlights}
                onContextsChange={handleContextsChange}
                readOnly
              />
            )}
            {sessionId && (
              <FormulaEditorPanel
                sessionId={sessionId}
                graph={data?.graph ?? null}
                variables={data?.variables ?? []}
                activeTermPickerId={activeTermPickerId}
                onTermPickerFocus={setActiveTermPickerId}
                onFormulasChange={handleFormulasChange}
                readOnly
              />
            )}
            {sessionId && (
              <ForcingPanel
                sessionId={sessionId}
                formulas={sharedFormulas}
                contexts={sharedContexts}
                scenarioCheck={data?.check ?? null}
                scenarioForces={data?.forces ?? null}
                scenarioForce={data?.force ?? null}
              />
            )}
            <EquationsPanel eqs={data?.graph?.equations ?? []} onPick={pickEq} />
            <DetailsPanel selected={selected} />
            <CommentPanel workspaceId={sessionId} />
          </div>
        </div>
      </div>
    </div>
  );
}

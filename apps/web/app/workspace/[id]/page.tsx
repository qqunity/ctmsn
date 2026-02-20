"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import { listScenarios, loadScenario, runScenario, renameWorkspace, undoNetwork, redoNetwork, getHistoryStatus, exportWorkspace, importWorkspace } from "@/lib/api";
import { LoadResponse, ScenarioSpec, Equation, ContextHighlights, FormulaInfo, NamedContextInfo, HistoryStatus } from "@/lib/types";
import { ScenarioBar } from "@/components/ScenarioBar";
import { GraphView, GraphViewHandle } from "@/components/GraphView";
import { StatusPanel } from "@/components/StatusPanel";
import { EquationsPanel } from "@/components/EquationsPanel";
import { DetailsPanel } from "@/components/DetailsPanel";
import { NetworkEditorPanel } from "@/components/NetworkEditorPanel";
import { CommentPanel } from "@/components/CommentPanel";
import { VariableEditorPanel } from "@/components/VariableEditorPanel";
import { ContextEditorPanel } from "@/components/ContextEditorPanel";
import { FormulaEditorPanel } from "@/components/FormulaEditorPanel";
import { ForcingPanel } from "@/components/ForcingPanel";
import { GraphLegend } from "@/components/GraphLegend";
import { LayoutSelector } from "@/components/LayoutSelector";
import { Tooltip } from "@/components/Tooltip";
import { HelpPanel } from "@/components/HelpPanel";
import { TOOLTIPS } from "@/lib/helpContent";

export default function WorkspacePage() {
  const { id } = useParams<{ id: string }>();
  const { user, loading: authLoading, logout } = useAuth();
  const router = useRouter();

  const [scenarios, setScenarios] = useState<ScenarioSpec[]>([]);
  const [scenario, setScenario] = useState<string>("");
  const [mode, setMode] = useState<string>("");
  const [derive, setDerive] = useState<boolean>(true);

  const [sessionId, setSessionId] = useState<string>(id);
  const [data, setData] = useState<LoadResponse | null>(null);
  const [selected, setSelected] = useState<any>(null);
  const [wsName, setWsName] = useState<string>("");
  const [editingName, setEditingName] = useState(false);
  const [nameInput, setNameInput] = useState("");
  const [pendingRequest, setPendingRequest] = useState(false);

  // New state for editors
  const [highlights, setHighlights] = useState<ContextHighlights | null>(null);
  const [activeTermPickerId, setActiveTermPickerId] = useState<string | null>(null);
  const [sharedFormulas, setSharedFormulas] = useState<FormulaInfo[]>([]);
  const [sharedContexts, setSharedContexts] = useState<NamedContextInfo[]>([]);
  const [historyStatus, setHistoryStatus] = useState<HistoryStatus>({ can_undo: false, can_redo: false, undo_count: 0, redo_count: 0 });
  const [graphLayout, setGraphLayout] = useState("cose");
  const [eqHighlights, setEqHighlights] = useState<ContextHighlights | null>(null);
  const [helpOpen, setHelpOpen] = useState(false);
  const graphRef = useRef<GraphViewHandle>(null);

  useEffect(() => {
    if (!authLoading && !user) router.replace("/login");
  }, [user, authLoading, router]);

  useEffect(() => {
    (async () => {
      const s = await listScenarios();
      setScenarios(s);
      if (s.length) setScenario(s[0].name);
    })();
  }, []);

  useEffect(() => {
    if (id && user) {
      runScenario({ session_id: id, derive: true })
        .then((payload) => {
          setData(payload);
          setSessionId(payload.session_id);
          setScenario(payload.scenario);
          setMode(payload.mode ?? "");
          setWsName(payload.name ?? "");
          getHistoryStatus(id).then(setHistoryStatus).catch(() => {});
        })
        .catch(() => {});
    }
  }, [id, user]);

  useEffect(() => {
    if (!pendingRequest) return;
    const handler = (e: BeforeUnloadEvent) => {
      e.preventDefault();
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, [pendingRequest]);

  async function handleLoad() {
    const payload = await loadScenario({
      scenario,
      mode: mode || null,
      derive,
    });
    setSessionId(payload.session_id);
    setData(payload);
    setWsName(payload.name ?? "");
    setSelected(null);
    setHighlights(null);
    router.replace(`/workspace/${payload.session_id}`);
  }

  async function handleRun() {
    if (!sessionId) return;
    const payload = await runScenario({ session_id: sessionId, derive });
    setData(payload);
    setWsName(payload.name ?? wsName);
  }

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
      // Find edges matching left, right, result labels
      for (const e of edges) {
        if (e.label === eq.left || e.label === eq.right || e.label === eq.result) {
          edgeIds.add(e.id);
          nodeIds.add(e.source);
          nodeIds.add(e.target);
        }
      }
      // Also look for mid-nodes from traces
      if (data.graph.traces?.comp2) {
        for (const t of data.graph.traces.comp2) {
          if (t.result === eq.result && t.left === eq.left && t.right === eq.right) {
            if (t.mid) nodeIds.add(t.mid);
          }
        }
      }
    } else {
      // compN: split chain by ";" and find edges by each label
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

  function handleGraphUpdate(newGraph: any) {
    if (data) {
      setData({ ...data, graph: newGraph });
    }
    if (sessionId) {
      getHistoryStatus(sessionId).then(setHistoryStatus).catch(() => {});
    }
  }

  async function handleUndo() {
    if (!sessionId || !historyStatus.can_undo) return;
    const res = await undoNetwork(sessionId);
    if (res.ok && res.graph && data) {
      setData({ ...data, graph: res.graph });
      setHistoryStatus({ can_undo: res.can_undo, can_redo: res.can_redo, undo_count: 0, redo_count: 0 });
    }
  }

  async function handleRedo() {
    if (!sessionId || !historyStatus.can_redo) return;
    const res = await redoNetwork(sessionId);
    if (res.ok && res.graph && data) {
      setData({ ...data, graph: res.graph });
      setHistoryStatus({ can_undo: res.can_undo, can_redo: res.can_redo, undo_count: 0, redo_count: 0 });
    }
  }

  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      const mod = e.metaKey || e.ctrlKey;
      if (mod && e.key === "z" && !e.shiftKey) {
        e.preventDefault();
        handleUndo();
      } else if (mod && e.key === "z" && e.shiftKey) {
        e.preventDefault();
        handleRedo();
      } else if (mod && e.key === "y") {
        e.preventDefault();
        handleRedo();
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  });

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
    if (activeTermPickerId) {
      // nothing — TermPicker handles this via its own dropdown
      // but we can still set selected for details
    }
    setSelected(x);
    setEqHighlights(null);
  }, [activeTermPickerId]);

  const handleFormulasChange = useCallback((formulas: FormulaInfo[]) => {
    setSharedFormulas(formulas);
  }, []);

  const handleContextsChange = useCallback((contexts: NamedContextInfo[]) => {
    setSharedContexts(contexts);
  }, []);

  async function handleNameSave() {
    if (!nameInput.trim() || nameInput.trim() === wsName) {
      setEditingName(false);
      return;
    }
    await renameWorkspace(sessionId, nameInput.trim());
    setWsName(nameInput.trim());
    setEditingName(false);
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

  function handleImportJson() {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".json";
    input.onchange = async () => {
      const file = input.files?.[0];
      if (!file) return;
      const text = await file.text();
      const data = JSON.parse(text);
      const result = await importWorkspace(data);
      router.push(`/workspace/${result.id}`);
    };
    input.click();
  }

  function handleExportPng() {
    const dataUrl = graphRef.current?.exportPng();
    if (!dataUrl) return;
    const a = document.createElement("a");
    a.href = dataUrl;
    a.download = `${wsName || "workspace"}.png`;
    a.click();
  }

  if (authLoading || !user) return null;

  return (
    <div className="flex h-screen flex-col">
      <div className="flex items-center gap-2 border-b bg-white px-3 py-2">
        <a href="/workspaces" className="text-sm text-blue-600 hover:underline mr-2">
          &larr; Назад
        </a>
        {editingName ? (
          <div className="flex items-center gap-1">
            <input
              type="text"
              value={nameInput}
              onChange={(e) => setNameInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleNameSave();
                if (e.key === "Escape") setEditingName(false);
              }}
              className="border rounded px-2 py-0.5 text-sm"
              autoFocus
            />
            <button onClick={handleNameSave} className="text-xs text-green-600 hover:underline">OK</button>
            <button onClick={() => setEditingName(false)} className="text-xs text-gray-500 hover:underline">Отмена</button>
          </div>
        ) : (
          <span
            className="text-sm font-medium cursor-pointer hover:text-blue-600"
            onClick={() => { setEditingName(true); setNameInput(wsName); }}
            title="Нажмите для переименования"
          >
            {wsName || "Без имени"}
          </span>
        )}
        <div className="flex items-center gap-1 ml-4">
          <Tooltip text={TOOLTIPS.undo} position="bottom">
            <button
              onClick={handleUndo}
              disabled={!historyStatus.can_undo}
              className="rounded px-2 py-1 text-sm disabled:opacity-30 hover:bg-gray-100"
            >
              &#x21A9;
            </button>
          </Tooltip>
          <Tooltip text={TOOLTIPS.redo} position="bottom">
            <button
              onClick={handleRedo}
              disabled={!historyStatus.can_redo}
              className="rounded px-2 py-1 text-sm disabled:opacity-30 hover:bg-gray-100"
            >
              &#x21AA;
            </button>
          </Tooltip>
          <LayoutSelector value={graphLayout} onChange={setGraphLayout} />
        </div>
        <div className="flex items-center gap-1 ml-2">
          <Tooltip text={TOOLTIPS.exportJson} position="bottom">
            <button
              onClick={handleExportJson}
              className="rounded px-2 py-1 text-xs hover:bg-gray-100"
            >
              &#x1F4E5; JSON
            </button>
          </Tooltip>
          <Tooltip text={TOOLTIPS.importJson} position="bottom">
            <button
              onClick={handleImportJson}
              className="rounded px-2 py-1 text-xs hover:bg-gray-100"
            >
              &#x1F4E4; JSON
            </button>
          </Tooltip>
          <Tooltip text={TOOLTIPS.exportPng} position="bottom">
            <button
              onClick={handleExportPng}
              className="rounded px-2 py-1 text-xs hover:bg-gray-100"
            >
              &#x1F4F7; PNG
            </button>
          </Tooltip>
        </div>
        <Tooltip text={TOOLTIPS.help} position="bottom">
          <button
            onClick={() => setHelpOpen(true)}
            className="rounded px-2 py-1 text-sm font-bold text-blue-600 hover:bg-blue-50 border border-blue-200"
          >
            ?
          </button>
        </Tooltip>
        <div className="flex-1" />
        <span className="text-sm text-gray-500">{user.username}</span>
        <button onClick={logout} className="text-sm text-red-600 hover:underline">
          Выйти
        </button>
      </div>

      <ScenarioBar
        scenarios={scenarios}
        scenario={scenario}
        setScenario={(s) => { setScenario(s); setMode(""); }}
        mode={mode}
        setMode={setMode}
        derive={derive}
        setDerive={setDerive}
        onNewSession={handleLoad}
        onLoad={handleLoad}
        onRun={handleRun}
      />

      <div className="flex flex-1 overflow-hidden">
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

        <div className="w-[460px] shrink-0 overflow-auto border-l bg-white p-4">
          <div className="space-y-4">
            <StatusPanel data={data} />
            {data?.variables && data.variables.length > 0 && (
              <VariableEditorPanel
                variables={data.variables}
                context={data.context ?? {}}
                sessionId={sessionId}
                graph={data?.graph ?? null}
                onUpdate={handleVariableUpdate}
              />
            )}
            {sessionId && (
              <ContextEditorPanel
                sessionId={sessionId}
                variables={data?.variables ?? []}
                onActivate={handleContextActivate}
                onHighlightsChange={setHighlights}
                onContextsChange={handleContextsChange}
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
              />
            )}
            {sessionId && (
              <ForcingPanel
                sessionId={sessionId}
                formulas={sharedFormulas}
                contexts={sharedContexts}
              />
            )}
            {sessionId && (
              <NetworkEditorPanel
                sessionId={sessionId}
                graph={data?.graph ?? null}
                onUpdate={handleGraphUpdate}
              />
            )}
            <EquationsPanel eqs={data?.graph?.equations ?? []} onPick={pickEq} />
            <DetailsPanel selected={selected} />
            <CommentPanel workspaceId={sessionId} />
          </div>
        </div>
      </div>
      <HelpPanel open={helpOpen} onClose={() => setHelpOpen(false)} scenario={scenario} />
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import { listScenarios, loadScenario, runScenario } from "@/lib/api";
import { LoadResponse, ScenarioSpec, Equation } from "@/lib/types";
import { ScenarioBar } from "@/components/ScenarioBar";
import { GraphView } from "@/components/GraphView";
import { StatusPanel } from "@/components/StatusPanel";
import { EquationsPanel } from "@/components/EquationsPanel";
import { DetailsPanel } from "@/components/DetailsPanel";
import { NetworkEditorPanel } from "@/components/NetworkEditorPanel";
import { CommentPanel } from "@/components/CommentPanel";

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
        })
        .catch(() => {});
    }
  }, [id, user]);

  async function handleLoad() {
    const payload = await loadScenario({
      scenario,
      mode: mode || null,
      derive,
    });
    setSessionId(payload.session_id);
    setData(payload);
    setSelected(null);
    router.replace(`/workspace/${payload.session_id}`);
  }

  async function handleRun() {
    if (!sessionId) return;
    const payload = await runScenario({ session_id: sessionId, derive });
    setData(payload);
  }

  function pickEq(eq: Equation) {
    setSelected(eq);
  }

  function handleGraphUpdate(newGraph: any) {
    if (data) {
      setData({ ...data, graph: newGraph });
    }
  }

  if (authLoading || !user) return null;

  return (
    <div className="flex h-screen flex-col">
      <div className="flex items-center gap-2 border-b bg-white px-3 py-2">
        <a href="/workspaces" className="text-sm text-blue-600 hover:underline mr-2">
          &larr; Назад
        </a>
        <span className="text-sm text-gray-500">{user.username}</span>
        <div className="flex-1" />
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
        <div className="flex-1">
          <GraphView graph={data?.graph ?? null} onSelect={setSelected} />
        </div>

        <div className="w-[460px] shrink-0 overflow-auto border-l bg-white p-4">
          <div className="space-y-4">
            <StatusPanel data={data} />
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
    </div>
  );
}

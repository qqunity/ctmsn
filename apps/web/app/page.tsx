"use client";

import { useEffect, useState } from "react";
import { listScenarios, loadScenario, newSession, runScenario } from "@/lib/api";
import { LoadResponse, ScenarioSpec, Equation } from "@/lib/types";
import { ScenarioBar } from "@/components/ScenarioBar";
import { GraphView } from "@/components/GraphView";
import { StatusPanel } from "@/components/StatusPanel";
import { EquationsPanel } from "@/components/EquationsPanel";
import { DetailsPanel } from "@/components/DetailsPanel";
import { NetworkEditorPanel } from "@/components/NetworkEditorPanel";

export default function Page() {
  const [scenarios, setScenarios] = useState<ScenarioSpec[]>([]);
  const [scenario, setScenario] = useState<string>("");
  const [mode, setMode] = useState<string>("");
  const [derive, setDerive] = useState<boolean>(true);

  const [sessionId, setSessionId] = useState<string>("");
  const [data, setData] = useState<LoadResponse | null>(null);
  const [selected, setSelected] = useState<any>(null);

  useEffect(() => {
    (async () => {
      const s = await listScenarios();
      setScenarios(s);
      if (s.length) setScenario(s[0].name);
    })();
  }, []);

  async function handleNewSession() {
    const sid = await newSession();
    setSessionId(sid);
    setSelected({ session_id: sid });
  }

  async function handleLoad() {
    const sid = sessionId || (await newSession());
    if (!sessionId) setSessionId(sid);

    const payload = await loadScenario({
      session_id: sid,
      scenario,
      mode: mode || null,
      derive,
    });
    setData(payload);
    setSelected(null);
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

  return (
    <div className="flex h-screen flex-col">
      <ScenarioBar
        scenarios={scenarios}
        scenario={scenario}
        setScenario={(s) => { setScenario(s); setMode(""); }}
        mode={mode}
        setMode={setMode}
        derive={derive}
        setDerive={setDerive}
        onNewSession={handleNewSession}
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
          </div>
        </div>
      </div>
    </div>
  );
}

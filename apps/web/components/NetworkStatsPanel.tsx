import { GraphPayload } from "@/lib/types";

interface NetworkStatsPanelProps {
  graph: GraphPayload | null;
}

export function NetworkStatsPanel({ graph }: NetworkStatsPanelProps) {
  const stats = [
    { label: "Концептов", value: graph?.nodes?.length ?? null },
    { label: "Предикатов", value: graph?.predicates?.length ?? null },
    { label: "Фактов", value: graph?.edges?.length ?? null },
    { label: "Уравнений", value: graph?.equations?.length ?? null },
  ];

  return (
    <div className="space-y-2">
      <div className="text-sm font-semibold">Статистика сети</div>
      <div className="grid grid-cols-4 gap-2">
        {stats.map((s) => (
          <div
            key={s.label}
            className="rounded-lg border bg-zinc-50 p-2 text-center"
          >
            <div className="text-lg font-bold text-zinc-800">
              {s.value !== null ? s.value : "\u2014"}
            </div>
            <div className="text-xs text-zinc-500">{s.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

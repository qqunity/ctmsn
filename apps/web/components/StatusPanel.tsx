import { LoadResponse } from "@/lib/types";

export function StatusPanel({ data }: { data: LoadResponse | null }) {
  return (
    <div className="space-y-2">
      <div className="text-sm font-semibold">Status</div>
      <pre className="whitespace-pre-wrap rounded-lg border bg-zinc-50 p-3 text-xs">
        {data
          ? JSON.stringify(
              { derivation: data.derivation, check: data.check, forces: data.forces, force: data.force },
              null,
              2
            )
          : "—"}
      </pre>
    </div>
  );
}

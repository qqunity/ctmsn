import { Equation } from "@/lib/types";

export function EquationsPanel({
  eqs,
  onPick,
}: {
  eqs: Equation[];
  onPick: (eq: Equation) => void;
}) {
  return (
    <div className="space-y-2">
      <div className="text-sm font-semibold">Equations</div>
      <div className="max-h-64 overflow-auto rounded-lg border bg-white">
        {eqs.length === 0 ? (
          <div className="p-3 text-sm text-zinc-500">No equations</div>
        ) : (
          <ul className="divide-y">
            {eqs.map((eq, i) => (
              <li
                key={i}
                className="cursor-pointer p-2 text-xs hover:bg-zinc-50"
                onClick={() => onPick(eq)}
              >
                {eq.kind === "comp2"
                  ? `${eq.result} = ${eq.right} ∘ ${eq.left}`
                  : `${eq.result} = ${eq.chain}`}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export function DetailsPanel({ selected }: { selected: any }) {
  if (!selected) {
    return (
      <div className="space-y-2">
        <div className="text-sm font-semibold">Details</div>
        <div className="rounded-lg border bg-zinc-50 p-3 text-xs text-zinc-500">
          Click a node/edge/equation
        </div>
      </div>
    );
  }

  const isNode = selected.id && selected.label && !selected.source;
  const isEdge = selected.source && selected.target;
  const isEquation = selected.kind && (selected.kind === "comp2" || selected.kind === "compN");

  return (
    <div className="space-y-2">
      <div className="text-sm font-semibold">Details</div>
      <div className="space-y-3 rounded-lg border bg-white p-3">
        {isNode && (
          <>
            <div>
              <div className="text-xs font-semibold text-zinc-600">Node</div>
              <div className="mt-1 text-sm font-medium">{selected.label || selected.id}</div>
              <div className="text-xs text-zinc-500">{selected.id}</div>
            </div>
            
            {selected.tags && selected.tags.length > 0 && (
              <div>
                <div className="text-xs font-semibold text-zinc-600">Tags</div>
                <div className="mt-1 flex flex-wrap gap-1">
                  {selected.tags.map((tag: string) => (
                    <span
                      key={tag}
                      className="rounded bg-blue-100 px-2 py-0.5 text-xs text-blue-700"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        {isEdge && (
          <>
            <div>
              <div className="text-xs font-semibold text-zinc-600">Edge</div>
              <div className="mt-1 text-sm">{selected.label}</div>
            </div>
            <div className="text-xs">
              <div className="text-zinc-600">From:</div>
              <div className="font-mono">{selected.source}</div>
            </div>
            <div className="text-xs">
              <div className="text-zinc-600">To:</div>
              <div className="font-mono">{selected.target}</div>
            </div>
            <div className="text-xs">
              <div className="text-zinc-600">Kind:</div>
              <div>
                <span
                  className={`inline-block rounded px-2 py-0.5 text-xs ${
                    selected.kind === "derived"
                      ? "bg-green-100 text-green-700"
                      : "bg-zinc-100 text-zinc-700"
                  }`}
                >
                  {selected.kind}
                </span>
              </div>
            </div>
          </>
        )}

        {isEquation && (
          <>
            <div>
              <div className="text-xs font-semibold text-zinc-600">Equation</div>
            </div>
            {selected.kind === "comp2" && (
              <div className="text-xs font-mono">
                {selected.result} = {selected.right} ∘ {selected.left}
              </div>
            )}
            {selected.kind === "compN" && (
              <div className="text-xs font-mono">
                {selected.result} = {selected.chain}
              </div>
            )}
          </>
        )}

        <details className="text-xs">
          <summary className="cursor-pointer text-zinc-500 hover:text-zinc-700">
            Raw JSON
          </summary>
          <pre className="mt-2 whitespace-pre-wrap rounded bg-zinc-50 p-2 text-xs">
            {JSON.stringify(selected, null, 2)}
          </pre>
        </details>
      </div>
    </div>
  );
}

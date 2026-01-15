export function DetailsPanel({ selected }: { selected: any }) {
  return (
    <div className="space-y-2">
      <div className="text-sm font-semibold">Details</div>
      <pre className="whitespace-pre-wrap rounded-lg border bg-zinc-50 p-3 text-xs">
        {selected ? JSON.stringify(selected, null, 2) : "Click a node/edge/equation"}
      </pre>
    </div>
  );
}

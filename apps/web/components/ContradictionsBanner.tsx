"use client";

export function ContradictionsBanner({ items }: { items: string[] }) {
  if (!items.length) return null;

  return (
    <div className="rounded-lg border border-yellow-400 bg-yellow-50 p-3 text-sm text-yellow-900">
      <div className="font-semibold mb-1">
        Обнаружены противоречия в сети ({items.length})
      </div>
      <ul className="list-disc list-inside space-y-0.5">
        {items.map((msg, i) => (
          <li key={i}>{msg}</li>
        ))}
      </ul>
    </div>
  );
}

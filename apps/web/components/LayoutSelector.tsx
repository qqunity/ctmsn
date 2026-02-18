"use client";

const LAYOUTS = [
  { value: "cose", label: "CoSE" },
  { value: "dagre", label: "Dagre" },
  { value: "circle", label: "Circle" },
  { value: "breadthfirst", label: "Breadthfirst" },
];

export function LayoutSelector({
  value,
  onChange,
}: {
  value: string;
  onChange: (layout: string) => void;
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="rounded border border-gray-300 px-2 py-1 text-xs bg-white"
      title="Layout графа"
    >
      {LAYOUTS.map((l) => (
        <option key={l.value} value={l.value}>
          {l.label}
        </option>
      ))}
    </select>
  );
}

"use client";

import { useState } from "react";

export function GraphLegend() {
  const [open, setOpen] = useState(false);

  return (
    <div className="absolute bottom-3 left-3 z-10">
      <button
        onClick={() => setOpen(!open)}
        className="rounded bg-white/90 border border-gray-300 px-2 py-1 text-xs shadow hover:bg-white"
      >
        {open ? "Скрыть легенду" : "Легенда"}
      </button>
      {open && (
        <div className="mt-1 rounded border border-gray-300 bg-white/95 p-3 text-xs shadow-lg space-y-2 min-w-[180px]">
          <div className="font-semibold text-gray-700 mb-1">Вершины</div>
          <div className="flex items-center gap-2">
            <span className="inline-block w-3 h-3 rounded-full bg-[#3b82f6]" />
            <span>Concept</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-block w-3 h-3 rounded-full bg-[#3b82f6] border-2 border-[#22c55e]" />
            <span>Подсвечен (контекст)</span>
          </div>

          <div className="font-semibold text-gray-700 mt-2 mb-1">Рёбра</div>
          <div className="flex items-center gap-2">
            <span className="inline-block w-6 h-0 border-t-2 border-[#64748b]" />
            <span>Edge</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-block w-6 h-0 border-t-2 border-dashed border-[#f59e0b]" />
            <span>Derived</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-block w-6 h-0 border-t-2 border-dotted border-[#8b5cf6]" />
            <span>Relation</span>
          </div>
        </div>
      )}
    </div>
  );
}

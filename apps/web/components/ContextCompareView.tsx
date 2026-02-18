"use client";

import { ContextCompareResult } from "@/lib/types";

type Props = {
  data: ContextCompareResult;
  onClose: () => void;
};

export function ContextCompareView({ data, onClose }: Props) {
  const allVarNames = new Set<string>();
  for (const ctx of data.contexts) {
    for (const key of Object.keys(ctx.context)) {
      allVarNames.add(key);
    }
  }
  const varNames = Array.from(allVarNames).sort();

  return (
    <div className="border rounded p-3 bg-white space-y-2">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-semibold">Сравнение контекстов</h4>
        <button onClick={onClose} className="text-xs text-gray-400 hover:text-gray-600">&times;</button>
      </div>
      <div className="overflow-x-auto">
        <table className="text-xs w-full border-collapse">
          <thead>
            <tr>
              <th className="border px-2 py-1 bg-gray-50 text-left">Переменная</th>
              {data.contexts.map((ctx) => (
                <th key={ctx.id} className="border px-2 py-1 bg-gray-50 text-left">{ctx.name}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {varNames.map((varName) => {
              const isDiff = varName in data.diff;
              return (
                <tr key={varName}>
                  <td className="border px-2 py-1 font-medium">{varName}</td>
                  {data.contexts.map((ctx) => {
                    const val = ctx.context[varName];
                    return (
                      <td
                        key={ctx.id}
                        className={`border px-2 py-1 ${isDiff ? "bg-amber-50 text-amber-800" : ""}`}
                      >
                        {val !== undefined ? String(val) : <span className="text-gray-300">—</span>}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

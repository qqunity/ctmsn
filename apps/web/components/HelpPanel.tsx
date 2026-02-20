"use client";

import { useState, useEffect, useCallback } from "react";
import {
  getTaskDescription,
  GLOSSARY,
  TRUTH_TABLES,
  type TruthValue,
} from "@/lib/helpContent";

type Tab = "task" | "logic" | "glossary";

interface HelpPanelProps {
  open: boolean;
  onClose: () => void;
  scenario?: string;
}

const TAB_LABELS: { key: Tab; label: string }[] = [
  { key: "task", label: "Задание" },
  { key: "logic", label: "Логика" },
  { key: "glossary", label: "Глоссарий" },
];

function truthColor(v: TruthValue): string {
  if (v === "T") return "bg-green-100 text-green-800";
  if (v === "F") return "bg-red-100 text-red-800";
  return "bg-yellow-100 text-yellow-800";
}

function truthLabel(v: TruthValue): string {
  if (v === "T") return "TRUE";
  if (v === "F") return "FALSE";
  return "UNKNOWN";
}

export function HelpPanel({ open, onClose, scenario }: HelpPanelProps) {
  const [tab, setTab] = useState<Tab>("task");

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    },
    [onClose]
  );

  useEffect(() => {
    if (!open) return;
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, handleKeyDown]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="bg-white rounded-lg shadow-xl w-[640px] max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b">
          <div className="flex gap-1">
            {TAB_LABELS.map(({ key, label }) => (
              <button
                key={key}
                onClick={() => setTab(key)}
                className={`px-3 py-1 rounded text-sm font-medium ${
                  tab === key
                    ? "bg-blue-100 text-blue-700"
                    : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                {label}
              </button>
            ))}
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl leading-none px-1"
          >
            &#x2715;
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-auto p-4 text-sm">
          {tab === "task" && <TaskTab scenario={scenario} />}
          {tab === "logic" && <LogicTab />}
          {tab === "glossary" && <GlossaryTab />}
        </div>
      </div>
    </div>
  );
}

function TaskTab({ scenario }: { scenario?: string }) {
  // Simple markdown-like rendering: split by lines, handle headers and lists
  const lines = getTaskDescription(scenario ?? "").split("\n");
  return (
    <div className="space-y-1 leading-relaxed">
      {lines.map((line, i) => {
        if (line.startsWith("### "))
          return (
            <h3 key={i} className="font-semibold text-base mt-3 mb-1">
              {line.slice(4)}
            </h3>
          );
        if (line.startsWith("## "))
          return (
            <h2 key={i} className="font-bold text-lg mt-4 mb-1">
              {line.slice(3)}
            </h2>
          );
        if (/^\d+\.\s\*\*/.test(line)) {
          const match = line.match(/^(\d+\.\s)\*\*(.+?)\*\*(.*)$/);
          if (match)
            return (
              <p key={i} className="ml-2">
                {match[1]}
                <strong>{match[2]}</strong>
                {match[3]}
              </p>
            );
        }
        if (line.startsWith("- "))
          return (
            <p key={i} className="ml-4">
              &bull; {line.slice(2)}
            </p>
          );
        if (line.trim() === "") return <div key={i} className="h-1" />;
        return <p key={i}>{line}</p>;
      })}
    </div>
  );
}

function LogicTab() {
  return (
    <div className="space-y-4">
      <p className="text-gray-600 mb-2">
        Трёхзначная логика Клини: TRUE (T), FALSE (F), UNKNOWN (U)
      </p>
      {TRUTH_TABLES.map((table) => (
        <div key={table.name}>
          <h3 className="font-semibold mb-1">{table.name}</h3>
          <table className="border-collapse text-center text-xs w-auto">
            <thead>
              <tr>
                {table.headers.map((h, i) => (
                  <th
                    key={i}
                    className="border border-gray-300 px-3 py-1 bg-gray-50 font-medium"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {table.rows.map((row, ri) => (
                <tr key={ri}>
                  {row.inputs.map((v, ci) => (
                    <td
                      key={ci}
                      className={`border border-gray-300 px-3 py-1 ${truthColor(v)}`}
                    >
                      {truthLabel(v)}
                    </td>
                  ))}
                  <td
                    className={`border border-gray-300 px-3 py-1 font-medium ${truthColor(row.output)}`}
                  >
                    {truthLabel(row.output)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
    </div>
  );
}

function GlossaryTab() {
  return (
    <div className="space-y-3">
      {GLOSSARY.map((entry) => (
        <div key={entry.term} className="border-b border-gray-100 pb-2">
          <div className="font-semibold">
            {entry.term}{" "}
            <span className="text-gray-400 font-normal text-xs">
              ({entry.termEn})
            </span>
          </div>
          <div className="text-gray-600 mt-0.5">{entry.definition}</div>
        </div>
      ))}
    </div>
  );
}

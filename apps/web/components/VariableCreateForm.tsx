"use client";

import { useState } from "react";
import { GraphPayload } from "@/lib/types";

type Props = {
  graph: GraphPayload | null;
  onSubmit: (data: { name: string; type_tag?: string; domain_type: string; domain: Record<string, any> }) => void;
  onCancel: () => void;
};

export function VariableCreateForm({ graph, onSubmit, onCancel }: Props) {
  const [name, setName] = useState("");
  const [typeTag, setTypeTag] = useState("");
  const [domainType, setDomainType] = useState<"enum" | "range" | "predicate">("enum");
  const [enumValues, setEnumValues] = useState<string[]>([]);
  const [enumInput, setEnumInput] = useState("");
  const [rangeMin, setRangeMin] = useState(0);
  const [rangeMax, setRangeMax] = useState(100);
  const [rangeInclusive, setRangeInclusive] = useState(true);
  const [predName, setPredName] = useState("");

  function addEnumValue(val: string) {
    const trimmed = val.trim();
    if (trimmed && !enumValues.includes(trimmed)) {
      setEnumValues([...enumValues, trimmed]);
    }
    setEnumInput("");
  }

  function handleSubmit() {
    if (!name.trim()) return;
    let domain: Record<string, any> = {};
    if (domainType === "enum") {
      domain = { values: enumValues };
    } else if (domainType === "range") {
      domain = { min: rangeMin, max: rangeMax, inclusive: rangeInclusive };
    } else {
      domain = { name: predName || "custom" };
    }
    onSubmit({
      name: name.trim(),
      type_tag: typeTag.trim() || undefined,
      domain_type: domainType,
      domain,
    });
  }

  const conceptIds = graph?.nodes?.map((n) => n.id) ?? [];

  return (
    <div className="border rounded p-3 bg-gray-50 space-y-2">
      <div className="flex gap-2">
        <input
          type="text"
          placeholder="Имя переменной"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="border rounded px-2 py-1 text-sm flex-1"
        />
        <input
          type="text"
          placeholder="Тип (опц.)"
          value={typeTag}
          onChange={(e) => setTypeTag(e.target.value)}
          className="border rounded px-2 py-1 text-sm w-24"
        />
      </div>

      <div className="flex gap-3 text-xs">
        {(["enum", "range", "predicate"] as const).map((dt) => (
          <label key={dt} className="flex items-center gap-1">
            <input
              type="radio"
              name="domainType"
              checked={domainType === dt}
              onChange={() => setDomainType(dt)}
            />
            {dt === "enum" ? "Перечисление" : dt === "range" ? "Диапазон" : "Предикат"}
          </label>
        ))}
      </div>

      {domainType === "enum" && (
        <div className="space-y-1">
          <div className="flex gap-1">
            <input
              type="text"
              placeholder="Добавить значение"
              value={enumInput}
              onChange={(e) => setEnumInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addEnumValue(enumInput); } }}
              className="border rounded px-2 py-1 text-xs flex-1"
            />
            <button onClick={() => addEnumValue(enumInput)} className="text-xs bg-blue-500 text-white px-2 py-1 rounded">+</button>
          </div>
          {conceptIds.length > 0 && (
            <select
              onChange={(e) => { if (e.target.value) addEnumValue(e.target.value); e.target.value = ""; }}
              className="border rounded px-2 py-1 text-xs w-full"
              defaultValue=""
            >
              <option value="">Из графа...</option>
              {conceptIds.map((cid) => (
                <option key={cid} value={cid}>{cid}</option>
              ))}
            </select>
          )}
          {enumValues.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {enumValues.map((v) => (
                <span key={v} className="bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded flex items-center gap-1">
                  {v}
                  <button onClick={() => setEnumValues(enumValues.filter((x) => x !== v))} className="text-blue-400 hover:text-red-500">&times;</button>
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {domainType === "range" && (
        <div className="flex gap-2 items-center">
          <input type="number" value={rangeMin} onChange={(e) => setRangeMin(Number(e.target.value))} className="border rounded px-2 py-1 text-xs w-20" />
          <span className="text-xs">—</span>
          <input type="number" value={rangeMax} onChange={(e) => setRangeMax(Number(e.target.value))} className="border rounded px-2 py-1 text-xs w-20" />
          <label className="flex items-center gap-1 text-xs">
            <input type="checkbox" checked={rangeInclusive} onChange={(e) => setRangeInclusive(e.target.checked)} />
            вкл.
          </label>
        </div>
      )}

      {domainType === "predicate" && (
        <input
          type="text"
          placeholder="Имя предиката"
          value={predName}
          onChange={(e) => setPredName(e.target.value)}
          className="border rounded px-2 py-1 text-xs w-full"
        />
      )}

      <div className="flex gap-2 justify-end">
        <button onClick={onCancel} className="text-xs text-gray-500 hover:underline">Отмена</button>
        <button onClick={handleSubmit} disabled={!name.trim()} className="text-xs bg-green-600 text-white px-3 py-1 rounded disabled:opacity-50">
          Создать
        </button>
      </div>
    </div>
  );
}

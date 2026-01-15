"use client";

import { useEffect, useRef } from "react";
import { GraphPayload } from "@/lib/types";

export function GraphView({
  graph,
  onSelect,
}: {
  graph: GraphPayload | null;
  onSelect: (x: any) => void;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<any>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    import("cytoscape").then(({ default: cytoscape }) => {
      if (cyRef.current) {
        cyRef.current.destroy();
      }

      const elements = !graph
        ? []
        : [
            ...graph.nodes.map((n) => ({ data: { id: n.id, label: n.label, tags: n.tags || [] } })),
            ...graph.edges.map((e) => ({
              data: { id: e.id, source: e.source, target: e.target, label: e.label, kind: e.kind },
            })),
          ];

      const cy = cytoscape({
        container: containerRef.current,
        elements,
        style: [
          {
            selector: "node",
            style: {
              label: "data(label)",
              "background-color": "#3b82f6",
              color: "#fff",
              "text-valign": "center",
              "text-halign": "center",
              width: "label",
              height: "label",
              "text-wrap": "wrap",
              "text-max-width": "120px",
              padding: "20px",
              "font-size": "14px",
              "font-weight": "500",
            } as any,
          },
          {
            selector: "edge",
            style: {
              label: "data(label)",
              "curve-style": "bezier",
              "target-arrow-shape": "triangle",
              "line-color": "#64748b",
              "target-arrow-color": "#64748b",
              "font-size": "10px",
            } as any,
          },
          {
            selector: 'edge[kind="derived"]',
            style: {
              "line-style": "dashed",
              "line-color": "#f59e0b",
              "target-arrow-color": "#f59e0b",
            } as any,
          },
          {
            selector: 'edge[kind="relation"]',
            style: {
              "line-style": "dotted",
              "line-color": "#8b5cf6",
              "target-arrow-color": "#8b5cf6",
              "font-size": "9px",
            } as any,
          },
        ],
        layout: { name: "cose" } as any,
      });

      cy.on("tap", "node", (evt) => onSelect(evt.target.data()));
      cy.on("tap", "edge", (evt) => onSelect(evt.target.data()));

      cyRef.current = cy;
    });

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, [graph, onSelect]);

  return <div ref={containerRef} className="h-full w-full" />;
}

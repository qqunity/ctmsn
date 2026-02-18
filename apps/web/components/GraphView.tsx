"use client";

import { useEffect, useRef, useImperativeHandle, forwardRef } from "react";
import { GraphPayload, ContextHighlights } from "@/lib/types";

export interface GraphViewHandle {
  exportPng(): string | null;
}

export const GraphView = forwardRef<
  GraphViewHandle,
  {
    graph: GraphPayload | null;
    onSelect: (x: any) => void;
    highlights?: ContextHighlights | null;
  }
>(function GraphView({ graph, onSelect, highlights }, ref) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<any>(null);

  useImperativeHandle(ref, () => ({
    exportPng() {
      if (!cyRef.current) return null;
      return cyRef.current.png({ full: true, scale: 2, bg: "white" });
    },
  }));

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
          {
            selector: "node.highlighted",
            style: {
              "border-width": 4,
              "border-color": "#22c55e",
              "border-style": "solid",
            } as any,
          },
          {
            selector: "edge.highlighted",
            style: {
              "line-color": "#22c55e",
              "target-arrow-color": "#22c55e",
              width: 3,
            } as any,
          },
        ],
        layout: { name: "cose" } as any,
      });

      cy.on("tap", "node", (evt: any) => onSelect(evt.target.data()));
      cy.on("tap", "edge", (evt: any) => onSelect(evt.target.data()));

      cyRef.current = cy;
    });

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, [graph, onSelect]);

  // Separate effect for highlights — does NOT re-render graph
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    cy.elements().removeClass("highlighted");

    if (highlights) {
      for (const nodeId of highlights.nodes) {
        cy.getElementById(nodeId).addClass("highlighted");
      }
      for (const edgeId of highlights.edges) {
        cy.getElementById(edgeId).addClass("highlighted");
      }
    }
  }, [highlights]);

  return <div ref={containerRef} className="h-full w-full" />;
});

"use client";

import { useEffect, useRef, useImperativeHandle, forwardRef } from "react";
import { GraphPayload, ContextHighlights } from "@/lib/types";

let dagreRegistered = false;

export interface GraphViewHandle {
  exportPng(): string | null;
}

export const GraphView = forwardRef<
  GraphViewHandle,
  {
    graph: GraphPayload | null;
    onSelect: (x: any) => void;
    highlights?: ContextHighlights | null;
    layout?: string;
    equationHighlights?: ContextHighlights | null;
  }
>(function GraphView({ graph, onSelect, highlights, layout = "cose", equationHighlights }, ref) {
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

    import("cytoscape").then(async ({ default: cytoscape }) => {
      if (!dagreRegistered) {
        const dagre = (await import("cytoscape-dagre")).default;
        cytoscape.use(dagre);
        dagreRegistered = true;
      }

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

      const layoutConfig: any =
        layout === "dagre"
          ? { name: "dagre", rankDir: "TB", nodeSep: 50, rankSep: 70 }
          : { name: layout };

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
          // Context highlights (green)
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
          // Equation highlights (orange)
          {
            selector: "node.eq-highlighted",
            style: {
              "border-width": 4,
              "border-color": "#f59e0b",
              "border-style": "solid",
            } as any,
          },
          {
            selector: "edge.eq-highlighted",
            style: {
              "line-color": "#f59e0b",
              "target-arrow-color": "#f59e0b",
              width: 3,
            } as any,
          },
          // Hover dimming
          {
            selector: "node.dimmed",
            style: { opacity: 0.15 } as any,
          },
          {
            selector: "edge.dimmed",
            style: { opacity: 0.15 } as any,
          },
          // Highlighted elements stay visible when dimmed
          {
            selector: "node.highlighted.dimmed",
            style: { opacity: 1 } as any,
          },
          {
            selector: "edge.highlighted.dimmed",
            style: { opacity: 1 } as any,
          },
          {
            selector: "node.eq-highlighted.dimmed",
            style: { opacity: 1 } as any,
          },
          {
            selector: "edge.eq-highlighted.dimmed",
            style: { opacity: 1 } as any,
          },
          // Hover active node
          {
            selector: "node.hover-active",
            style: {
              "border-width": 4,
              "border-color": "#2563eb",
              "border-style": "solid",
              opacity: 1,
            } as any,
          },
          // Hover neighbor nodes
          {
            selector: "node.hover-neighbor",
            style: {
              "border-width": 3,
              "border-color": "#60a5fa",
              "border-style": "solid",
              opacity: 1,
            } as any,
          },
          // Neighbor edges stay visible
          {
            selector: "edge.hover-neighbor",
            style: { opacity: 1 } as any,
          },
        ],
        layout: layoutConfig,
      });

      cy.on("tap", "node", (evt: any) => onSelect(evt.target.data()));
      cy.on("tap", "edge", (evt: any) => onSelect(evt.target.data()));

      // Hover highlight
      cy.on("mouseover", "node", (evt: any) => {
        const node = evt.target;
        const neighborhood = node.neighborhood().add(node);
        cy.elements().addClass("dimmed");
        neighborhood.removeClass("dimmed");
        node.addClass("hover-active");
        node.neighborhood("node").addClass("hover-neighbor");
        node.neighborhood("edge").addClass("hover-neighbor");
      });

      cy.on("mouseout", "node", () => {
        cy.elements().removeClass("dimmed hover-active hover-neighbor");
      });

      cyRef.current = cy;
    });

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, [graph, onSelect, layout]);

  // Separate effect for context highlights
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

  // Separate effect for equation highlights
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    cy.elements().removeClass("eq-highlighted");

    if (equationHighlights) {
      for (const nodeId of equationHighlights.nodes) {
        cy.getElementById(nodeId).addClass("eq-highlighted");
      }
      for (const edgeId of equationHighlights.edges) {
        cy.getElementById(edgeId).addClass("eq-highlighted");
      }
    }
  }, [equationHighlights]);

  return <div ref={containerRef} className="h-full w-full" />;
});

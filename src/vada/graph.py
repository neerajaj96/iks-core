"""Phase 4 — Vada directed knowledge graph G_Vada = (V, E, W). Stdlib only."""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class VadaGraph:
    nodes: dict = field(default_factory=dict)
    edges: list = field(default_factory=list)

    def add_node(self, nid: str, **attrs):
        self.nodes[nid] = attrs

    def add_edge(self, src: str, dst: str, kind: str, fallacy: str = "none",
                 ref: str = "", locus: str = "", weight: float = 0.5):
        self.edges.append({"from": src, "to": dst, "kind": kind,
                           "fallacy": fallacy, "ref": ref, "locus": locus, "weight": weight})

    def attack_paths(self, src: str, dst: str, limit: int = 10) -> list[list[str]]:
        adj = {}
        for e in self.edges:
            adj.setdefault(e["from"], []).append(e["to"])
        paths, stack = [], [(src, [src])]
        while stack and len(paths) < limit:
            cur, path = stack.pop()
            if cur == dst:
                paths.append(path)
                continue
            for nxt in adj.get(cur, []):
                if nxt not in path:
                    stack.append((nxt, path + [nxt]))
        return paths

    def summary(self) -> str:
        return f"G_Vada: |V|={len(self.nodes)} |E|={len(self.edges)}"


def load_seed() -> VadaGraph:
    base = Path(__file__).resolve().parents[2]
    g = VadaGraph()
    for name in ("vada_nodes.json", "vada_edges.json"):
        p = base / "data" / name
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            if name.startswith("vada_nodes"):
                for n in data:
                    g.add_node(n["id"], **{k: v for k, v in n.items() if k != "id"})
            else:
                for e in data:
                    g.add_edge(e["from"], e["to"], e.get("kind", "khandana"),
                               e.get("fallacyCharged", "none"), e.get("refutationTextId", ""),
                               e.get("locus", ""), e.get("weight", 0.5))
    return g

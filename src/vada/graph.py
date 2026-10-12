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

    def filter_by_katha(self, katha: str) -> "VadaGraph":
        sub = VadaGraph()
        for nid, attrs in self.nodes.items():
            if attrs.get("katha", "Vada") == katha:
                sub.add_node(nid, **attrs)
        for e in self.edges:
            if e["from"] in sub.nodes and e["to"] in sub.nodes:
                sub.edges.append(e)
        return sub

    def weighted_degree(self) -> dict[str, float]:
        deg: dict[str, float] = {n: 0.0 for n in self.nodes}
        for e in self.edges:
            w = float(e.get("weight", 0.5))
            deg[e["from"]] = deg.get(e["from"], 0.0) + w
            deg[e["to"]] = deg.get(e["to"], 0.0) + w
        return deg

    def pagerank(self, damping: float = 0.85, iters: int = 50) -> dict[str, float]:
        nodes = list(self.nodes)
        n = len(nodes)
        if n == 0:
            return {}
        rank = {v: 1.0 / n for v in nodes}
        out_w: dict[str, float] = {v: 0.0 for v in nodes}
        for e in self.edges:
            out_w[e["from"]] = out_w.get(e["from"], 0.0) + float(e.get("weight", 0.5))
        for _ in range(iters):
            dangling = sum(rank[v] for v in nodes if out_w.get(v, 0.0) <= 0.0)
            new = {v: (1 - damping) / n + damping * dangling / n for v in nodes}
            for e in self.edges:
                s, t, w = e["from"], e["to"], float(e.get("weight", 0.5))
                if out_w.get(s, 0.0) > 0:
                    new[t] += damping * rank[s] * w / out_w[s]
            rank = new
        return rank

    def fallacy_histogram(self) -> dict[str, int]:
        h: dict[str, int] = {}
        for e in self.edges:
            f = e.get("fallacy", "none")
            h[f] = h.get(f, 0) + 1
        return h

    def d3_export(self) -> dict:
        idx = {nid: i for i, nid in enumerate(self.nodes)}
        return {
            "nodes": [{"id": nid, "group": a.get("katha", "Vada"),
                       "label": a.get("siddhanta", nid)[:60]} for nid, a in self.nodes.items()],
            "links": [{"source": idx[e["from"]], "target": idx[e["to"]],
                       "kind": e.get("kind"), "value": e.get("weight", 0.5)}
                      for e in self.edges if e["from"] in idx and e["to"] in idx],
        }


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

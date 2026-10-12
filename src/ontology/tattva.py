"""Phase 2C — Samkhya 25-tattva DAG + guna simplex + satkaryavada."""
from __future__ import annotations

TATTVAS_25 = (["Purusa", "Prakrti-mula", "buddhi", "ahankara", "manas"]
              + [f"jnanendriya-{i}" for i in range(5)]
              + [f"karmendriya-{i}" for i in range(5)]
              + [f"tanmatra-{i}" for i in range(5)]
              + [f"mahabhuta-{i}" for i in range(5)])

EVOLUTION_EDGES = [
    ("Prakrti-mula", "buddhi"), ("buddhi", "ahankara"),
    ("ahankara", "manas"),
] + [( "ahankara", f"jnanendriya-{i}") for i in range(5)] \
  + [("ahankara", f"karmendriya-{i}") for i in range(5)] \
  + [("ahankara", f"tanmatra-{i}") for i in range(5)] \
  + [(f"tanmatra-{i}", f"mahabhuta-{i}") for i in range(5)]


def ancestors(node: str) -> list[str]:
    """Walk evolution DAG backwards to mula-prakrti."""
    parents = {c: p for p, c in EVOLUTION_EDGES}
    out, cur = [], node
    while cur in parents:
        cur = parents[cur]
        out.append(cur)
    return out


def guna_simplex(s: float, r: float, t: float, tol: float = 1e-9) -> bool:
    return abs((s + r + t) - 1.0) < tol and min(s, r, t) >= 0.0


def satkaryavada_holds(effect: str) -> bool:
    """Every vyakta effect pre-exists as sakti in avyakta prakrti."""
    return effect in TATTVAS_25 and effect != "Purusa"


def kaivalya(purusa_discrimination: bool) -> bool:
    """viveka: Purusa != any prakrti-vikrti."""
    return bool(purusa_discrimination)

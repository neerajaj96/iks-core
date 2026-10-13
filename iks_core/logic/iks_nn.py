"""Phase 3 — Navya-Nyaya intensional operators (IKS-NN).

Deliberately NOT reduced to plain FOL: relations carry limiter (avacchedaka),
counter-correlate (pratiyogin) and locus (anuyogin) roles.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Limiter:
    """Avacchedaka: property phi limiting x. A_phi(x)."""
    prop: str
    target: str

    def render(self) -> str:
        return f"A_{self.prop}({self.target})"


@dataclass(frozen=True)
class Pratiyogita:
    """Counter-correlateness: x is absentee delimited by phi under R."""
    absentee: str
    limiter_prop: str
    relation: str

    def render(self) -> str:
        return f"PR_{self.limiter_prop},{self.relation}({self.absentee})"


@dataclass(frozen=True)
class Anuyogita:
    """Correlateness: y is locus-side of R-absence."""
    locus: str
    relation: str

    def render(self) -> str:
        return f"AN_{self.relation}({self.locus})"


@dataclass(frozen=True)
class Absence:
    """Four relational absences (samsargabhava + anyonyabhava)."""
    kind: str  # "prag" | "dhvamsa" | "atyanta" | "anyonya"
    content: str
    relation: str = "samyoga"
    limiter: str = ""
    locus: str = ""
    t0: str = "t0"

    def render(self) -> str:
        if self.kind == "prag":
            return f"¬_p {self.content}(t) for t < {self.t0}"
        if self.kind == "dhvamsa":
            return f"¬_d {self.content}(t) for t > {self.t0}"
        if self.kind == "atyanta":
            return f"¬_a^[{self.relation},{self.limiter}] {self.content} @ {self.locus}"
        return f"{self.content} ≠_id {self.locus}"


@dataclass(frozen=True)
class Vyapti:
    hetu: str
    hetu_limiter: str
    sadhya: str
    sadhya_limiter: str

    def render(self) -> str:
        return (f"{self.hetu} ⇉[{self.hetu_limiter}→{self.sadhya_limiter}] {self.sadhya}")


def occurs_in(x: str, y: str, relation: str) -> str:
    return f"{x} ⊏_{relation} {y}"


def hill_inference() -> dict[str, str]:
    """E1: parvato vahniman dhumat — with limiters."""
    v = Vyapti("dhuma", "dhumatva", "vahni", "vahnitva")
    return {
        "pratijna": occurs_in("vahni[A_vahnitva]", "parvata", "samyoga"),
        "hetu": occurs_in("dhuma[A_dhumatva]", "parvata", "samyoga"),
        "udaharana": f"{v.render()}  ex: mahanasa (anvaya) / hrada (vyatireka)",
        "upanaya": "ayam-api dhumavan + vyapti-smrti",
        "nigamana": "tasmad parvato vahniman",
        "sab dabodha": "vahnitva-prakaraka, parvata-visesyaka, samyoga-samsargaka anumiti",
    }


def floor_absence() -> str:
    """bhutale ghato nasti — canonical absolute absence."""
    a = Absence("atyanta", "ghata", relation="samyoga", limiter="ghatatva", locus="bhutala")
    pr = Pratiyogita("ghata", "ghatatva", "samyoga")
    an = Anuyogita("bhutala", "samyoga")
    return f"{a.render()}  with {pr.render()}, {an.render()}"


def laghava_check(candidate_limiters: list[str], working: set[str]) -> str:
    """Simplicity meta-rule: keep minimal limiter doing real exclusion work."""
    minimal = [c for c in candidate_limiters if c in working]
    return minimal[0] if minimal else ""

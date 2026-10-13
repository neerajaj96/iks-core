"""Phase 2D — Syadvada saptabhangi 7-state truth matrix.

Not fuzzy logic: standpoint-indexed bivalence + inexpressibility U.
Standpoint n = (dravya, ksetra, kala, bhava).
"""
from __future__ import annotations
from dataclasses import dataclass

SYAD_NAMES = {
    1: "syad-asti",
    2: "syan-nasti",
    3: "syad-asti-nasti (kramena, sequential)",
    4: "syad-avaktavya (saha, simultaneous)",
    5: "syad-asti-avaktavya",
    6: "syan-nasti-avaktavya",
    7: "syad-asti-nasti-avaktavya",
}


@dataclass(frozen=True)
class Standpoint:
    dravya: str
    ksetra: str
    kala: str
    bhava: str


def evaluate(p_n1: int, p_n2: int, simultaneous: bool, mode: str) -> int:
    """Derive saptabhangi member (1-7) from base evaluations.

    p_n1: T_{n1}(p) in {0,1} (svadravya standpoint)
    p_n2: T_{n2}(p) in {0,1} (paradravya standpoint)
    simultaneous: whether assertion attempted in one pada (saha) -> U-family
    mode: 'asti' | 'nasti' | 'asti-nasti' | 'avaktavya' | 'asti-avaktavya'
          | 'nasti-avaktavya' | 'asti-nasti-avaktavya'
    Consistency with (p_n1, p_n2) is enforced; mismatch raises ValueError.
    """
    needs_1 = mode in ("asti", "asti-nasti", "asti-avaktavya", "asti-nasti-avaktavya")
    needs_0 = mode in ("nasti", "asti-nasti", "nasti-avaktavya", "asti-nasti-avaktavya")
    needs_u = "avaktavya" in mode
    if needs_1 and p_n1 != 1:
        raise ValueError(f"mode {mode} requires p_n1=1, got {p_n1}")
    if needs_0 and p_n2 != 0:
        raise ValueError(f"mode {mode} requires p_n2=0, got {p_n2}")
    if needs_u != simultaneous:
        raise ValueError(f"mode {mode} requires simultaneous={needs_u}")
    table = {
        ("asti", False): 1, ("nasti", False): 2, ("asti-nasti", False): 3,
        ("avaktavya", True): 4, ("asti-avaktavya", True): 5,
        ("nasti-avaktavya", True): 6, ("asti-nasti-avaktavya", True): 7,
    }
    return table[(mode, simultaneous)]


def pot_example() -> dict[int, str]:
    return {
        1: "ghato mrttikaya asti (pot exists as clay — svadravya)",
        2: "ghato kanaka-rupena nasti (pot does not exist as gold — paradravya)",
        3: "kramena ubhayam (successively both)",
        4: "saha vacana-asakyatvat avaktavyah (simultaneous assertion inexpressible)",
        5: "asti + avaktavya", 6: "nasti + avaktavya", 7: "asti + nasti + avaktavya",
    }


def negate(member: int) -> int:
    """Negation flips 1<->2, 5<->6, fixes 4, maps 3<->3, 7<->7."""
    return {1: 2, 2: 1, 3: 3, 4: 4, 5: 6, 6: 5, 7: 7}[member]

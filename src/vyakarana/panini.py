"""Vyakarana pilot: Aṣṭādhyāyī as attribute grammar G=(V,Sigma,R,S) + sphoṭa colimit."""
from __future__ import annotations

RULES = [
    ("3.1.68 kartari śap", "bhū + laṭ/tip → bhū + a + ti"),
    ("guṇa 1.1.3/7.3.84", "bhū + a + ti → bho + a + ti"),
    ("av 6.1.78 eco'yavāyāvaḥ", "bho + a + ti → bhav + a + ti = bhavati"),
    ("vipratiṣedhe paraṃ kāryam 1.4.2", "conflict → posterior rule wins"),
]


def derive_bhavati() -> list[str]:
    steps = ["bhu + laṬ + tip (vivakṣā: kartā, vartamāna)"]
    for name, desc in RULES[:3]:
        steps.append(f"[{name}] {desc}")
    return steps


def sphota_colimit(dhvani_variants: list[str]) -> dict:
    """Multiple dhvani realizations map to one sphoṭa object (colimit)."""
    return {"dhvani_paths": dhvani_variants, "sphota": "S_vākya(bhavati)",
            "property": "colimit: all paths converge; pratibhā = section S→cognition"}

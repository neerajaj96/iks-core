"""Sahitya pilot: Rasa-sutra vector operator + dhvani layers."""
from __future__ import annotations

STHAYI_8 = ["rati", "hasa", "soka", "krodha", "utsaha", "bhaya", "jugupsa", "vismaya"]
RASAS_9 = ["srngara", "hasya", "karuna", "raudra", "vira", "bhayanaka", "bibhatsa", "adbhuta", "santa"]
VYABHICARI_33 = 33


def rasa(vibhava: float, anubhava: float, vyabhicari_sum: float, sthayi: str,
         sahrdaya: float = 1.0) -> dict:
    """R = Phi(V,A,Y) ⊙ S0. Phi = sadharanikarana (depersonalization gain)."""
    if sthayi not in STHAYI_8 + ["sama"]:
        raise ValueError(f"unknown sthayi {sthayi}")
    phi = sahrdaya * (0.4 * vibhava + 0.3 * anubhava + 0.3 * (vyabhicari_sum / VYABHICARI_33))
    mapping = dict(zip(STHAYI_8, RASAS_9[:8]))
    mapping["sama"] = "santa"
    return {"rasa": mapping[sthayi], "intensity": round(phi, 4),
            "residue": "camatkara (non-formalizable)"}


def dhvani_layers(vacya: str, laksya: str, vyangya: str, vyangya_weight: float, vacya_weight: float) -> str:
    if vyangya_weight > vacya_weight:
        return f"dhvani-kavya (uttama): vyangya '{vyangya}' dominates vacya '{vacya}'"
    if vyangya_weight == vacya_weight:
        return "gunibhutavyangya (madhyama)"
    return "citra-kavya (adhama)"

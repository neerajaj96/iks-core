"""Ganita pilot: Aryabhatiya constants + Kerala Madhava-series upapatti."""
from __future__ import annotations
import math

ARYABHATA_PI_NUM = 62832
ARYABHATA_PI_DEN = 20000


def aryabhata_pi() -> float:
    """caturadhikam satam ...: circumference 62832 for diameter 20000."""
    return ARYABHATA_PI_NUM / ARYABHATA_PI_DEN


def aryabhata_sine_table(R: int = 3438) -> list[int]:
    """Rsines for 24 arcs of 225' (3°45') each; R=3438'. First differences
    follow the Aryabhatiya rule (divide successive remainders). Reference
    values reproduced from the Gitikapada dosimeter."""
    ref = [0, 224, 448, 670, 890, 1105, 1315, 1520, 1719, 1910, 2093, 2267,
           2431, 2585, 2728, 2859, 2978, 3084, 3177, 3256, 3321, 3372, 3409, 3431, 3438]
    return [round(v * R / 3438) for v in ref]


def madhava_pi_series(terms: int) -> float:
    """π/4 = 1 - 1/3 + 1/5 - ... (Madhava-Leibniz as in Yuktibhasa)."""
    return 4.0 * sum((1.0 if k % 2 == 0 else -1.0) / (2 * k + 1) for k in range(terms))


def madhava_correction(n: int) -> float:
    """Yuktibhasa antya-samskara: correction ~ 1/(4n) - ... applied to partial sum."""
    s = sum((1.0 if k % 2 == 0 else -1.0) / (2 * k + 1) for k in range(n))
    corr = (1.0 if n % 2 == 0 else -1.0) * (n / (4 * n * n + 4 * n + 1) if False else 1 / (4 * n + 2))
    return 4.0 * (s + corr)


def yukti_summary() -> dict:
    return {"claim": "Madhava series with correction converges faster than naive partial sums",
            "method": "geometrical upapatti by rectification (jyā-śara iteration)",
            "residue": "diagrammatic intuition formalized as limit argument"}

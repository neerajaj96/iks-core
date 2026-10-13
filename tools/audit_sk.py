"""v2.9 WS3: SK audit — verse-integrity + key-phrase presence per karika.

Key phrases below were transcribed FROM the vendored GRETIL SK text
(tools/fixtures/sa_IzvarakRSNa-sAMkhyakArikA.xml), not from memory.
Comparison: light normalization (diacritics/hyphens/whitespace folded).

Usage: python3 tools/audit_sk.py   (exit 1 on any failure; CI-gated)
"""
from __future__ import annotations
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tools" / "fixtures" / "sa_IzvarakRSNa-sAMkhyakArikA.xml"

# verse -> distinctive phrase (plain-ascii normalized form of the edition text)
KEYS = {
 3: "mulaprakrtiravikrti", 4: "trividhampramanam", 9: "satkaryam",
 11: "trigunamaviveki", 12: "prityapritivisadatmakah",
 13: "sattvamlaghuprakasakam", 17: "samghatapararthatvat",
 18: "purusabahutvamsiddham", 19: "saksitvam", 20: "tatsamyogad",
 21: "pangvandhavad", 22: "ahamkaras", 23: "adhyavasayobuddhir",
 24: "abhimano", 25: "ekadasakahpravartatevaikrtad",
 38: "tanmatranyavisesas", 40: "purvotpannamasaktam",
 44: "dharmenagamanamurdhvam", 45: "vairagyatprakrtilayah",
 46: "pratyayasargo", 47: "pancaviparyayabheda",
 50: "adhyatmikascatasrah", 51: "uhahsabdoadhyayanam",
 53: "astavikalpodaivas", 54: "urdhvamsattvavisalas",
 57: "vatsavivrddhinimittam", 59: "rangasyadarsayitva",
 62: "namucyate", 64: "nasminamenaham",
 66: "drstamayety", 67: "cakrabhramavad", 68: "kaivalyam",
 69: "guhyamparamarsina", 70: "etatpavitramagryam",
}


def norm(s: str) -> str:
    t = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z]", "", t)


def main() -> int:
    x = FIX.read_text(encoding="utf-8")
    verses = {}
    for m in re.finditer(r'<lg xml:id="SK_(\d+)">(.*?)</lg>', x, re.S):
        verses[int(m.group(1))] = norm(re.sub(r"<[^>]+>", " ", m.group(2)))
    fails = []
    if sorted(verses)[:70] != list(range(1, 71)):
        fails.append(f"verse range broken: {sorted(verses)[:5]}...{sorted(verses)[-3:]}")
    for n, phrase in KEYS.items():
        if n not in verses:
            fails.append(f"SK-{n}: verse missing in fixture")
        elif norm(phrase) not in verses[n]:
            fails.append(f"SK-{n}: phrase {phrase!r} not found")
    # our corpus must cover K01..K70 (SK-4 merged seed covers karika 4)
    import json
    ours = set(r["id"] for r in json.loads((ROOT / "data" / "sutras.json").read_text())
               if r["id"].startswith("SK-K") or r["id"] == "SK-4")
    want = {f"SK-K{n:02d}" for n in range(1, 71) if n != 4} | {"SK-4"}
    if ours != want:
        fails.append(f"SK-K coverage gap: missing {sorted(want - ours)[:5]} "
                     f"extra {sorted(ours - want)[:5]}")
    print(f"SK audit: {len(KEYS)} phrases, {len(ours)}/70 karikas, {len(fails)} failures")
    for f in fails:
        print("FAIL", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

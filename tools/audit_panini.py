"""v2.7 Phase 3: systematic Panini audit against the sūtrapāṭha index fixture.

Fixture: tools/fixtures/panini_sutrapatha.txt — lines 'A X.Y.Z<TAB><devanāgarī text>',
extracted from sanskritdocuments sortable index (+ AVG cross-links), Oct 2026.
Comparison is skeleton-based (Devanāgarī→IAST map, drop spaces/case/marks).

Usage:
  python3 tools/audit_panini.py --extract RAW_DUMP   # rebuild fixture (one-time)
  python3 tools/audit_panini.py --report             # PASS/FAIL/MISSING per A-* record
Exit code 1 if any FAIL (wording/number mismatch on verbatim/famous-gist records).
"""
from __future__ import annotations
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tools" / "fixtures" / "panini_sutrapatha.txt"

DEVA = {
    "अ": "a", "आ": "a", "इ": "i", "ई": "i", "उ": "u", "ऊ": "u",
    "ऋ": "r", "ॠ": "r", "ऌ": "l", "ए": "e", "ऐ": "ai", "ओ": "o", "औ": "au",
    "ा": "a", "ि": "i", "ी": "i", "ु": "u", "ू": "u", "ृ": "r", "ॄ": "r",
    "े": "e", "ै": "ai", "ो": "o", "ौ": "au", "ं": "m", "ः": "", "ँ": "",
    "्": "", "ऽ": "", "।": "", "॥": "",
    "क": "ka", "ख": "kha", "ग": "ga", "घ": "gha", "ङ": "na",
    "च": "ca", "छ": "cha", "ज": "ja", "झ": "jha", "ञ": "na",
    "ट": "ta", "ठ": "tha", "ड": "da", "ढ": "dha", "ण": "na",
    "त": "ta", "थ": "tha", "द": "da", "ध": "dha", "न": "na",
    "प": "pa", "फ": "pha", "ब": "ba", "भ": "bha", "म": "ma",
    "य": "ya", "र": "ra", "ल": "la", "व": "va",
    "श": "sa", "ष": "sa", "स": "sa", "ह": "ha",
    "ळ": "la", "क्ष": "ksa", "ज्ञ": "jna",
}
# Our corpus uses undiacriticized IAST: fold the same distinctions there too.


def fold(s: str) -> str:
    t = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    t = re.sub(r"[^a-z' ]", " ", t)
    # our undiacriticized IAST writes visarga as word-final -ah/-ih/-uh/-eh/-oh
    toks = [re.sub(r"([aiueo])h$", r"\1", w) for w in t.split()]
    t = "".join(toks)
    t = t.replace("a", "").replace("'", "")
    t = re.sub(r"([a-z])h\1h", r"\1h", t)  # aspirate-cluster variants (chch/chha)
    return re.sub(r"(.)\1", r"\1", t)  # print-variant geminates (karmma/karma)


def deva_skeleton(s: str) -> str:
    out = []
    for ch in s:
        if ch in DEVA:
            out.append(DEVA[ch])
        elif ch.strip() == "" or ch in ".-–—/()[]":
            continue
        else:
            out.append(ch)
    return fold("".join(out))


def iast_skeleton(s: str) -> str:
    return fold(s)


def extract(raw_path: Path) -> None:
    lines = raw_path.read_text(encoding="utf-8", errors="replace").splitlines()
    pairs = {}
    for i, ln in enumerate(lines):
        m = re.search(r"Sktdocs-(\d+\.\d+\.\d+);", ln)
        if not m:
            continue
        for j in range(i + 1, min(i + 6, len(lines))):
            if re.search(r"[\u0900-\u097F]{3,}", lines[j]):
                pairs[m.group(1)] = re.sub(r"\s+", " ", lines[j]).strip()
                break
    FIX.parent.mkdir(parents=True, exist_ok=True)
    with open(FIX, "w", encoding="utf-8") as f:
        for k in sorted(pairs, key=lambda x: tuple(map(int, x.split(".")))):
            f.write(f"A {k}\t{pairs[k]}\n")
    print(f"fixture: {len(pairs)} sutras -> {FIX}")


def report() -> int:
    idx = {}
    for ln in FIX.read_text(encoding="utf-8").splitlines():
        if "\t" in ln:
            k, v = ln.split("\t", 1)
            idx[k[2:]] = v
    data = json.loads((ROOT / "data" / "sutras.json").read_text(encoding="utf-8"))
    fails, missing, passes, skipped = [], [], 0, 0
    for r in sorted(data, key=lambda x: x["id"]):
        if not r["id"].startswith("A-") or r["id"].startswith("A-PADA"):
            continue
        if "·" in r.get("adhyaNotation", ""):
            skipped += 1  # range/cluster record: number-existence only, not word-compare
            continue
        m = re.search(r"A (\d+\.\d+\.\d+)", r.get("adhyaNotation", ""))
        if not m:
            missing.append((r["id"], "no parsable notation"))
            continue
        num = m.group(1)
        if num not in idx:
            missing.append((r["id"], f"{num} not in fixture"))
            continue
        if deva_skeleton(idx[num]) == iast_skeleton(r.get("sanskrit", "")):
            passes += 1
        else:
            fails.append((r["id"], num, r.get("sanskrit", ""), idx[num]))
    print(f"PASS {passes} | FAIL {len(fails)} | MISSING {len(missing)} | RANGE-SKIP {skipped}")
    for fid, num, ours, theirs in fails:
        print(f"FAIL {fid} [{num}]\n  ours:   {ours}\n  edition:{theirs}")
    for fid, why in missing:
        print(f"MISSING {fid}: {why}")
    return 1 if fails else 0


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--extract":
        extract(Path(sys.argv[2]))
    elif len(sys.argv) == 2 and sys.argv[1] == "--report":
        sys.exit(report())
    else:
        print(__doc__)

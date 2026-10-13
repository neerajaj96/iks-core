"""v2.9 WS1: scripted full ingestion of NS + YS wording from vendored GRETIL texts.

Tiers (per approved policy): wording = verbatim (machine-extracted, skeleton-
spot-checked); translation = concise locator-gist, translationTier topic-digest,
translationSource iks-gist. Existing hand records always win (setdefault).
Every ingested record carries editionRef (exact GRETIL verse id).

Usage: python3 tools/ingest_gretil.py   (idempotent)
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.ingest import write_json, mirror_to_docs

ROOT = Path(__file__).resolve().parents[1]
NS_FIX = ROOT / "tools" / "fixtures" / "sa_gautama-nyAyasUtra.xml"
YS_FIX = ROOT / "tools" / "fixtures" / "sa_pataJjali-yogasUtra.xml"

NS_KIND = [("siddhānta", "Established view"), ("pūrvapakṣa", "Objection"),
           ("lakṣaṇa", "Definition"), ("uddeśa", "Enumeration"),
           ("parīkṣā", "Examination"), ("prakaraṇa", "Topic")]
YS_PADA = {"1": "samādhi", "2": "sādhana", "3": "vibhūti", "4": "kaivalya"}


def kind_of(tag: str) -> str:
    for k, en in NS_KIND:
        if k in tag:
            return en
    return "Sūtra"


def hook(text: str, n: int = 5) -> str:
    return " ".join(text.split()[:n])


def parse_ns() -> list[dict]:
    x = NS_FIX.read_text(encoding="utf-8")
    # sūtras sometimes share one <p>; split on number marks instead
    marks = [(m.group(1), m.end()) for m in re.finditer(r"(\d+\.\d+\.\d+):", x)]
    ctx = ""
    # prakaraṇa context: track last [...] before each position
    brackets = [(m.group(0), m.start()) for m in re.finditer(r"\[.*?\]", x)]
    out = []
    for i, (num, start) in enumerate(marks):
        end = marks[i + 1][1] - len(num) - 1 if i + 1 < len(marks) else start + 500
        seg = x[start:end]
        seg = re.sub(r"<[^>]+>", " ", seg)
        tm = re.search(r"\{(.*?)\}", seg)
        tag = tm.group(1) if tm else ""
        body = re.sub(r"\{.*?\}", "", seg)
        body = re.sub(r"\[.*?\]", "", body)
        body = re.sub(r"\[.*$", "", body).strip()  # unclosed trailing label
        body = re.sub(r"\s+", " ", body).strip()
        cands = [btext.strip("[]") for btext, bpos in brackets
                 if bpos < start - len(num) - 1 and not re.search(r"\(\d", btext)]
        ctx = next((c for c in reversed(cands)
                    if "prakaraṇa" in c or "parīkṣā" in c), cands[-1] if cands else "")
        rec = {"id": f"NS-{num}", "textId": "NS", "adhyaNotation": f"NS {num}",
               "sanskrit": body,
               "translation": f"{kind_of(tag)} ({ctx}): {hook(body)}…",
               "padarthasMentioned": [], "pramanasInvoked": [],
               "confidence": "verbatim", "translationTier": "topic-digest",
               "translationSource": "iks-gist",
               "sourceNote": f"GRETIL NS {num}; gist from prakaraṇa tag",
               "verifyAgainst": "GRETIL NS (sa_gautama-nyAyasUtra)",
               "editionRef": f"GRETIL-NS {num}"}
        out.append(rec)
    return out


def parse_ys() -> list[dict]:
    x = YS_FIX.read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r"<l>(.*?)\|\|\s*YS_(\d+\.\d+)\s*\|\|</l>", x, re.S):
        body = re.sub(r"\s+", " ", m.group(1)).strip()
        num = m.group(2)
        pada = YS_PADA.get(num.split(".")[0], "")
        out.append({"id": f"YS-{num}", "textId": "YS", "adhyaNotation": f"YS {num}",
                    "sanskrit": body,
                    "translation": f"Yogasūtra ({pada} pāda): {hook(body)}…",
                    "padarthasMentioned": [], "pramanasInvoked": [],
                    "confidence": "verbatim", "translationTier": "topic-digest",
                    "translationSource": "iks-gist",
                    "sourceNote": f"GRETIL YS {num}; gist pending hand translation",
                    "verifyAgainst": "GRETIL YS (sa_pataJjali-yogasUtra)",
                    "editionRef": f"GRETIL-YS {num}"})
    return out


def main():
    import re
    import unicodedata
    old = json.loads((ROOT / "data" / "sutras.json").read_text(encoding="utf-8"))
    by_id = {r["id"]: r for r in old}
    # full verbatim records supersede these two gist clusters (identical content)
    for drop in ("NS-1.1-PRETYA", "NS-1.1-DUHKHA"):
        by_id.pop(drop, None)
    added = {"NS": 0, "YS": 0}
    for r in parse_ns() + parse_ys():
        if r["id"] not in by_id:
            by_id[r["id"]] = r
            added[r["textId"]] += 1
        elif by_id[r["id"]].get("translationSource") == "iks-gist":
            # self-healing rerun: refresh machine-extracted wording/translation
            by_id[r["id"]].update({k: r[k] for k in
                                   ("sanskrit", "translation", "editionRef", "sourceNote")})
    out = sorted(by_id.values(), key=lambda r: (r["textId"], r["adhyaNotation"]))
    # link genuine edition repetitions (same wording, different numbers)
    def norm(s):
        return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", s)
                      .encode("ascii", "ignore").decode().lower())
    seen = {}
    for r in out:
        key = (r["textId"], norm(r.get("sanskrit", "")))
        if key in seen and seen[key] != r["id"]:
            r["sameWordingAs"] = seen[key]
        else:
            seen.setdefault(key, r["id"])
    write_json(ROOT / "data" / "sutras.json", out)
    mirror_to_docs(ROOT, "sutras.json", out)
    ns = sum(1 for r in out if r["textId"] == "NS")
    ys = sum(1 for r in out if r["textId"] == "YS")
    print(f"sutras {len(old)} -> {len(out)} (+NS {added['NS']}, +YS {added['YS']}); totals NS={ns} YS={ys}")


if __name__ == "__main__":
    main()

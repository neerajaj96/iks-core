"""v2.9 WS1: scripted full ingestion of NS + YS wording from vendored GRETIL texts.

NOTE (2026-10): Python 3.14 changed `$` to match end-of-string ONLY (no longer
before newlines). All strip-to-end patterns below use `[\s\S]*\Z` so behavior
is identical on 3.10–3.14. Do not reintroduce `.*$` idioms.
"""

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
JS_FIX = ROOT / "tools" / "fixtures" / "sa_jaimini-mImAMsAsUtra.xml"
BS_FIX = ROOT / "tools" / "fixtures" / "sa_bAdarAyaNa-brahmasUtra.xml"

NS_KIND = [("siddhānta", "Established view"), ("pūrvapakṣa", "Objection"),
           ("lakṣaṇa", "Definition"), ("uddeśa", "Enumeration"),
           ("parīkṣā", "Examination"), ("prakaraṇa", "Topic")]
YS_PADA = {"1": "samādhi", "2": "sādhana", "3": "vibhūti", "4": "kaivalya"}
BS_ADH = {"1": "samanvaya", "2": "avirodha", "3": "sādhana", "4": "phala"}
# ingested twins that duplicate superior hand records -> skip (hand wins)
SKIP_TWINS = {"BS-1.1.1", "BS-1.1.2"}


def norm_key(textid: str, sanskrit: str) -> tuple:
    import unicodedata
    return (textid, re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", sanskrit)
                           .encode("ascii", "ignore").decode().lower()))


def parse_js() -> list[dict]:
    x = JS_FIX.read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r"<l>(.*?)/\s*Jaim_(\d+),([\d.]+)\*?\s*/</l>", x, re.S):
        body = re.sub(r"\s+", " ", m.group(1)).strip()
        body = re.sub(r"/\s*Jaim_[\s\S]*\Z", "", body).strip()  # stray variant marker
        body = re.sub(r"\(\S{1,4}\)", "", body)
        num = f"{m.group(2)}.{m.group(3)}"
        out.append({"id": f"JS-{num}", "textId": "JS", "adhyaNotation": f"JS {num}",
                    "sanskrit": body,
                    "translation": f"Mīmāṃsā (adhyāya {m.group(2)}): {hook(body)}…",
                    "padarthasMentioned": [], "pramanasInvoked": [],
                    "confidence": "verbatim", "translationTier": "topic-digest",
                    "translationSource": "iks-gist",
                    "sourceNote": f"GRETIL JS {num}; gist pending hand translation",
                    "verifyAgainst": "GRETIL JS (sa_jaimini-mImAMsAsUtra)",
                    "editionRef": f"GRETIL-JS {num}"})
    return out


def parse_bs() -> list[dict]:
    x = BS_FIX.read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r"<l>(.*?)\|\s*BBs_(\d+),([\d.]+)\s*\|</l>", x, re.S):
        body = re.sub(r"\s+", " ", m.group(1)).strip()
        body = re.sub(r"\(\S{1,4}\)", "", body).strip()
        num = f"{m.group(2)}.{m.group(3)}"
        out.append({"id": f"BS-{num}", "textId": "BS", "adhyaNotation": f"BS {num}",
                    "sanskrit": body,
                    "translation": f"Vedānta ({BS_ADH.get(m.group(2), 'brahman')}): {hook(body)}…",
                    "padarthasMentioned": [], "pramanasInvoked": [],
                    "confidence": "verbatim", "translationTier": "topic-digest",
                    "translationSource": "iks-gist",
                    "sourceNote": f"GRETIL BS {num}; gist pending hand translation",
                    "verifyAgainst": "GRETIL BS (sa_bAdarAyaNa-brahmasUtra)",
                    "editionRef": f"GRETIL-BS {num}"})
    return out


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
        body = re.sub(r"\[.+\Z", "", body, flags=re.S).strip()  # unclosed trailing label
        body = re.sub(r"\(iti ny[\s\S]*\Z", "", body).strip()  # closing colophon
        body = re.sub(r"<p[\s\S]*\Z", "", body).strip()
        body = re.sub(r"\(\S{1,4}\)", "", body)  # editorial ditto/lacuna marks
        body = re.sub(r"\s+", " ", body).strip()
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
    added = {"NS": 0, "YS": 0, "JS": 0, "BS": 0}
    existing_keys = {norm_key(x["textId"], x.get("sanskrit", "")) for x in by_id.values()}
    for r in parse_ns() + parse_ys() + parse_js() + parse_bs():
        if r["id"] in SKIP_TWINS:
            continue
        if r["id"] not in by_id:
            if norm_key(r["textId"], r["sanskrit"]) in existing_keys:
                continue  # hand record with same wording wins
            by_id[r["id"]] = r
            existing_keys.add(norm_key(r["textId"], r["sanskrit"]))
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
    counts = {t: sum(1 for r in out if r["textId"] == t) for t in ("NS", "YS", "JS", "BS")}
    print(f"sutras {len(old)} -> {len(out)} (+{added}); totals {counts}")


if __name__ == "__main__":
    main()

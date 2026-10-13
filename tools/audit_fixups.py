"""v2.7 Phases 1-2: fix confirmed errors, merge duplicate/near-duplicate pairs
(transplanting richer content into canonical records), remap term refs,
stamp audit metadata. Idempotent; preserves sort order.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.ingest import write_json, mirror_to_docs

ROOT = Path(__file__).resolve().parents[1]
AUDIT = {"edition": "sanskritdocuments sūtrapāṭha + sortable index / GRETIL", "date": "2026-10"}

# --- Phase 1: wording fixes ---
FIXES = {
    "A-11162": {"sanskrit": "pratyayalope pratyayalaksanam",
                "translation": "On affix-elision, affix-conditioned operations still apply (pratyayalakṣaṇa)",
                "sourceNote": "CORRECTED v2.7: was 'pratyayah' (that is 3.1.1); verified vs sūtrapāṭha 1.1.62"},
    "A-2122": {"sanskrit": "tatpurusah",
               "translation": "Tatpuruṣa compound (determinative; case-relation pattern)",
               "sourceNote": "CORRECTED v2.7: pasted text belonged to 1.2.42; verified vs index 2.1.22"},
}
SPOTCHECKED = ["YS-1.2", "YS-1.7", "YS-3.1", "YS-3.2", "A-1142", "A-1103", "A-311",
               "A-14122", "A-2346", "A-4182", "A-4192"]

# --- v2.8: NS wording fixes verified vs GRETIL NS (sa_gautama-nyAyasUtra) ---
NS_FIXES = {
    "NS-1.1.5": {"sanskrit": "atha tatpurvakam trividham anumanam purvavat sesavat samanyatodrstam ca",
                 "sourceNote": "CORRECTED v2.8: garbled 'purvavacchesavat' fixed; verified vs GRETIL NS 1.1.5"},
    "NS-1.1.10": {"sanskrit": "icchadvesaprayatnasukhaduhkhajnanani atmano lingam",
                  "sourceNote": "CORRECTED v2.8: 'jnananam' -> 'jnanani'; verified vs GRETIL NS 1.1.10"},
    "NS-1.1-PRAV": {"sanskrit": "pravrttir vagbuddhisarira-arambhah",
                    "translation": "Activity: initiation by speech, cognition, body (no manas in NS 1.1.17)",
                    "sourceNote": "CORRECTED v2.8: dropped manas per GRETIL NS 1.1.17"},
}
NS_AUDIT = {"edition": "GRETIL NS (sa_gautama-nyAyasUtra)", "date": "2026-10"}
NS_SPOT = ["NS-1.1.1", "NS-1.1.2", "NS-1.1.3", "NS-1.1.4", "NS-1.1.6", "NS-1.1.7",
           "NS-1.1.8", "NS-1.1.9", "NS-1.1.11", "NS-1.1.12", "NS-1.1.14", "NS-1.1.15",
           "NS-1.1.16", "NS-1.1.32", "NS-1.2-SAV", "NS-1.2-VIR", "NS-1.2-PRAK",
           "NS-1.2-SADH", "NS-1.2-KALA", "NS-1.2-VADA", "NS-1.2-JALPA", "NS-1.2-VIT"]

# --- Phase 2: merges (drop -> keep), transplanting richer fields into keeper ---
MERGES = {
    "A-1113": "A-1103",
    "A-LAT": "A-32123",
    "SK-K04": "SK-4",
    "SK-SID": "SKK-SAMJNA",
    "SK-1": "SK-K01", "SK-2": "SK-K02", "SK-3": "SK-K03", "SK-9": "SK-K09",
    "SK-11": "SK-K11", "SK-12": "SK-K12", "SK-13": "SK-K13", "SK-17": "SK-K17",
    "SK-19": "SK-K19", "SK-21": "SK-K21", "SK-57": "SK-K57",
}
TRANSPLANT = ["sanskrit", "translation", "logicalForm"]
TERM_REMAP = {"SK-17": "SK-K17", "SK-19": "SK-K19", "SK-3": "SK-K03"}


def main():
    sutras = json.loads((ROOT / "data" / "sutras.json").read_text(encoding="utf-8"))
    by_id = {r["id"]: r for r in sutras}

    for rid, patch in FIXES.items():
        by_id[rid].update(patch)
        by_id[rid]["audited"] = dict(AUDIT)
        by_id[rid]["confidence"] = "verbatim"
    for rid in SPOTCHECKED:
        if rid in by_id:
            by_id[rid]["audited"] = dict(AUDIT)

    for rid, patch in NS_FIXES.items():
        if rid in by_id:
            by_id[rid].update(patch)
            by_id[rid]["audited"] = dict(NS_AUDIT)
    for rid in NS_SPOT:
        if rid in by_id:
            by_id[rid]["audited"] = dict(NS_AUDIT)
    # jati/nigraha enumerations verified vs GRETIL NS 5.1.1/5.2.1 compounds
    for r in by_id.values():
        if r["id"].startswith("NS-1.2-JATI") or r["id"].startswith("NS-1.2-NIG"):
            r["audited"] = dict(NS_AUDIT)
            r["sourceNote"] = (r.get("sourceNote", "") + " | names verified vs NS 5.1.1/5.2.1").strip(" |")

    # --- v2.9 WS2: translation tiers. Hand translations reviewed (famous lines
    # checked against standard published translations); rule-glosses stay gist.
    REVIEWED = ["UP-AIT", "BS-111", "BS-112", "UP-CHAND314", "GITA-1866", "GITA-247",
                "GITA-47", "UP-KATHA", "UP-MUND", "UP-ISA", "JS-112", "KAS-RITI",
                "KP-KAVYA", "MMK-24", "MMK-DED", "NS-1.1.1", "NS-1.1.15", "NS-1.1.16",
                "NS-1.1.3", "NS-1.1.32", "NS-1.1.4", "NS-1.1.7", "NAT-RASA", "SK-4",
                "TA-1.1", "VS-1.1.5", "VS-1.1.7", "YS-1.12", "YS-1.2", "YS-1.7",
                "YS-2.46", "YS-3.1", "YS-3.2", "NS-1.1.2", "NS-1.1.5", "NS-1.1.6",
                "NS-1.1.8", "NS-1.1.9", "NS-1.1.10", "NS-1.1.11", "NS-1.1.12",
                "NS-1.1.14",                 "UP-TAT", "UP-AHAM", "GITA-220", "SK-K09",
                "SK-K17", "SK-K19", "SK-K40", "SK-K57", "SK-K64", "SK-K68", "SK-K03"]
    for r in by_id.values():
        if r.get("translationSource") == "iks-gist":
            r.setdefault("translationTier", "topic-digest")
            continue
        r["translationSource"] = "hand"
        if r["id"] in REVIEWED:
            r["translationTier"] = "reviewed"
        else:
            r.setdefault("translationTier", "famous-gist")

    for drop, keep in MERGES.items():
        if drop in by_id and keep in by_id:
            d, k = by_id[drop], by_id[keep]
            for f in TRANSPLANT:
                if f in d and (f not in k or len(str(d[f])) > len(str(k.get(f, "")))):
                    k[f] = d[f]
            k["sourceNote"] = (k.get("sourceNote", "") + f" | merged seed {drop} (v2.7)").strip(" |")
            k["audited"] = dict(AUDIT)
            del by_id[drop]

    terms = json.loads((ROOT / "data" / "terms.json").read_text(encoding="utf-8"))
    for t in terms:
        t["definitionSutras"] = [TERM_REMAP.get(s, s) for s in t.get("definitionSutras", [])]
    write_json(ROOT / "data" / "terms.json", terms)
    mirror_to_docs(ROOT, "terms.json", terms)

    out = sorted(by_id.values(), key=lambda r: (r["textId"], r["adhyaNotation"]))
    write_json(ROOT / "data" / "sutras.json", out)
    mirror_to_docs(ROOT, "sutras.json", out)
    print(f"sutras {len(sutras)} -> {len(out)} "
          f"(fixed {len(FIXES)}, merged {len(MERGES)}, spot-stamped {len(SPOTCHECKED)})")


if __name__ == "__main__":
    main()

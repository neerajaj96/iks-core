"""v2.8: MMK 27-chapter clusters (6 records), Samkhya/Yoga vada debut (+2/+2)."""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.ingest import provenance, normalize_iast, write_json, mirror_to_docs

ROOT = Path(__file__).resolve().parents[1]
T = "topic-digest"

R = [
 ("MMK-CH01-07", "MMK", "MMK 1-7 · pratyaya/gati/cakṣus/skandha/dhātu/rāga/saṃskṛta", "condition, motion, sense, aggregates, elements, passion, compounded"),
 ("MMK-CH08-13", "MMK", "MMK 8-13 · karman/pūrva/agni/pūrvāpara/duḥkha/saṃskāra", "agent/action, past, fire-fuel, limits, suffering, formations"),
 ("MMK-CH14-19", "MMK", "MMK 14-19 · saṃsarga/svabhāva/bandha/karman/ātman/kāla", "contact, own-being, bondage, karmic fruit, self, time"),
 ("MMK-CH20-23", "MMK", "MMK 20-23 · sāmagrī/sambhava/tathāgata/viparyāsa", "assemblage, becoming, thus-gone, errors"),
 ("MMK-CH24-25", "MMK", "MMK 24-25 · satya/nirvāṇa", "truths and emptiness (24.18), nirvāṇa examination"),
 ("MMK-CH26-27", "MMK", "MMK 26-27 · dvādaśāṅga/dṛṣṭi", "twelvefold arising, views"),
]
VNODES = [
 ("arg-sk-satkarya", "SK", ["SK-K09"], "Satkāryavāda reply: effect pre-exists; milk-curd regularity (vs kṣaṇabhaṅga)", "Vada", "Pratitantra"),
 ("arg-ys-citta", "YS", ["YS-1.2"], "Citta-vṛtti stability + saṃskāra continuity (vs momentariness)", "Vada", "Pratitantra"),
]
VEDGES = [
 ("e32", "arg-sk-satkarya", "arg-ts-ksanika", "uddhara", "Satpratipaksa", "SK", "satkarya-vada (k9)", 0.6),
 ("e33", "arg-ys-citta", "arg-ts-ksanika", "khandana", "Viruddha", "YS", "citta-smrti thread", 0.55),
]


def main():
    old = json.loads((ROOT / "data" / "sutras.json").read_text(encoding="utf-8"))
    by_id = {r["id"]: r for r in old}
    for rid, not_, tr in [(r[0], r[2], r[3]) for r in R]:
        if rid not in by_id:
            p = provenance(T, f"{not_} (canon-6)")
            by_id[rid] = {"id": rid, "textId": "MMK", "adhyaNotation": not_,
                          "sanskrit": not_.split("·")[1].strip() if "·" in not_ else not_,
                          "translation": "MMK chapters: " + tr,
                          "padarthasMentioned": ["Abhava"], "pramanasInvoked": [],
                          "confidence": p["tier"], "sourceNote": p["note"],
                          "verifyAgainst": "MMK chapter titles (editions)"}
    out = sorted(by_id.values(), key=lambda r: (r["textId"], r["adhyaNotation"]))
    write_json(ROOT / "data" / "sutras.json", out)
    mirror_to_docs(ROOT, "sutras.json", out)

    nodes = json.loads((ROOT / "data" / "vada_nodes.json").read_text(encoding="utf-8"))
    nids = {n["id"] for n in nodes}
    for nid, text, refs, sidd, katha, kind in VNODES:
        if nid not in nids:
            nodes.append({"id": nid, "textId": text, "sutraRefs": refs, "siddhanta": sidd,
                          "katha": katha, "siddhantaKind": kind})
    edges = json.loads((ROOT / "data" / "vada_edges.json").read_text(encoding="utf-8"))
    eids = {e["id"] for e in edges}
    for eid, fr, to, kind, fal, ref, loc, w in VEDGES:
        if eid not in eids:
            edges.append({"id": eid, "from": fr, "to": to, "kind": kind,
                          "fallacyCharged": fal, "refutationTextId": ref, "locus": loc, "weight": w})
    for name, obj in (("vada_nodes.json", nodes), ("vada_edges.json", edges)):
        write_json(ROOT / "data" / name, obj)
        mirror_to_docs(ROOT, name, obj)
    print(f"sutras {len(old)} -> {len(out)}; nodes {len(nodes)}; edges {len(edges)}")


if __name__ == "__main__":
    main()

"""Canon round 4 (balance stretch): NS Books 3-5 depth, YS practice records,
Dhvanyaloka 4 udyotas + Natya completion, Carvaka vada presence (SDS node + 2 edges).
Honest tiers throughout.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.ingest import provenance, normalize_iast, write_json, mirror_to_docs

ROOT = Path(__file__).resolve().parents[1]
V, F, T = "verbatim", "famous-gist", "topic-digest"

# (id, textId, notation, tier, sanskrit, translation, pada, pram, logic)
R = [
 # ---- NS Book 3: prameya-pariksa ----
 ("NS-3.1-ATMAN", "NS", "NS 3.1 · ātma-śarīra-bheda", T, "atma-sarira-bheda",
  "Self distinct from body: cognition/desire outlast limbs; dehātmavāda refuted", ["prameya"], ["Anumana"], ""),
 ("NS-3.1-IND2", "NS", "NS 3.1 · indriya-nānātva", T, "indriya-nanatva (vrtti-bhedat)",
  "Plurality of senses from function-difference (against eka-indriya)", ["prameya"], ["Anumana"], ""),
 ("NS-3.1-ARTHA", "NS", "NS 3.1 · artha-niyama", T, "gandhadi-niyama",
  "Sense-object fixity: smell-earth etc. against Buddhist flux", ["prameya"], ["Pratyaksa"], ""),
 ("NS-3.2-BUDDHI", "NS", "NS 3.2 · buddhi-anityatva", T, "buddhi-guna-anitya",
  "Cognition as non-eternal quality of self (vs Sāṅkhya buddhi-tattva)", ["prameya"], ["Anumana"], ""),
 ("NS-3.2-MANAS2", "NS", "NS 3.2 · manas-smṛti", T, "manas-smrti-hetu",
  "Mind as auxiliary cause of memory/attention", ["prameya"], [], ""),
 # ---- NS Book 4: dosa/duhkha/apavarga ----
 ("NS-4.1-DOSA2", "NS", "NS 4.1 · doṣa-moha-mūla", T, "moho mulam dosanam",
  "Delusion as root of attachment/aversion; kleśa mechanics", ["prameya"], [], ""),
 ("NS-4.1-DUHKHA2", "NS", "NS 4.1 · duḥkha-sarvatra", T, "duhkha-anusangi janma",
  "Suffering entwined with birth itself (against good-only views)", ["prameya"], [], ""),
 ("NS-4.2-TATTVA", "NS", "NS 4.2 · tattva-jñāna-phala", T, "tattvajnanan nihsreyasam",
  "True knowledge of the categories yields the highest good (restated)", ["Nyaya16"], [], ""),
 ("NS-4.2-APAV2", "NS", "NS 4.2 · apavarga-svarūpa", T, "apavarga-acaitanya? (duhkha-nivrtti)",
  "Release as suffering's end; unconsciousness-charge answered", ["prameya"], [], ""),
 # ---- NS Book 5: jati/nigraha detail ----
 ("NS-5.1-JATIV", "NS", "NS 5.1 · jāti-dṛṣṭānta", T, "jati-bheda-udaharana",
  "Worked futile objections (similarity, excess, unarising...) answered", ["jati"], [], ""),
 ("NS-5.2-NIGRAHA2", "NS", "NS 5.2 · nigraha-prayoga", T, "nigrahasthana-prayoga",
  "Points of defeat applied: deviation, irrelevance, repetition...", ["nigrahasthana"], [], ""),
 ("NS-5.2-ANTA", "NS", "NS 5.2 · śāstra-samāpti", T, "sastra-samapti-phala",
  "Treatise closure: fruit of mastering debate science", ["Nyaya16"], [], ""),
 # ---- YS practice ----
 ("YS-1.12", "YS", "YS 1.12", V, "abhyasavairagyabhyam tannirodhah",
  "Stillings by practice and dispassion", ["Tattva"], []),
 ("YS-2.46", "YS", "YS 2.46", V, "sthirasukhamasanam", "Seat steady and easy", ["Tattva"], []),
 ("YS-2.49", "YS", "YS 2.49 · prāṇāyāma", T, "svasaprasvasayor gativicchedah",
  "Breath-regulation as fourth limb adjunct", ["Tattva"], []),
 ("YS-3.1", "YS", "YS 3.1", V, "desabandhascittasya dharana", "Fixing mind on a place: dhāraṇā", ["Tattva"], []),
 ("YS-3.2", "YS", "YS 3.2", V, "tatra pratyayaikatanata dhyanam", "Unbroken flow there: dhyāna", ["Tattva"], []),
 ("YS-3.3", "YS", "YS 3.3 · samādhi", T, "tadevartham atranirbhasam ...",
  "When only the object shines: samādhi; three make saṃyama", ["Tattva"], []),
 # ---- Dhvanyaloka 4 udyotas ----
 ("DHA-U1", "DhvA", "Dhvanyāloka 1 · dhvani-svarūpa", F, "kavyasyatma dhvanih ...",
  "Soul of poetry is suggestion; deniers (abhāva/alaṅkāra-reduction) answered", ["Dhvani"], [], "(Sv,Sl,Svya)"),
 ("DHA-U2", "DhvA", "Dhvanyāloka 2 · dhvani-bheda", T, "vastu-alankara-rasa-dhvani",
  "Three suggestions: fact, figure, rasa (rasa-dhvani supreme)", ["Dhvani"], [], ""),
 ("DHA-U3", "DhvA", "Dhvanyāloka 3 · vyaṅgya-prayoga", T, "samlaksya-asamlaksya-krama",
  "Ordered/unordered suggestion; guṇībhūta contexts", ["Dhvani"], [], ""),
 ("DHA-U4", "DhvA", "Dhvanyāloka 4 · pratibhā-hetu", T, "pratibha-vyutpatti-abhyasa",
  "Poet's genius, learning, practice as poetry's causes", ["Dhvani"], [], ""),
 # ---- Natya completion ----
 ("NAT-BHAVA", "Natya", "NŚ 7 · bhāva-saṅgraha", F, "unapancasat bhavah (8+33+8)",
  "Forty-nine emotions total: durable, transient, sattvic", ["Rasa"], [], ""),
 ("NAT-SATTVIKA", "Natya", "NŚ 7 · sāttvika", T, "astau sattvikah (stambha ...)",
  "Eight involuntary states (tears, horripilation...)", ["Rasa"], [], ""),
 ("NAT-VIGHNA", "Natya", "NŚ/Abhinava · rasa-vighna", T, "rasa-vighna-nivarana",
  "Obstacles to relish removed (Abhinavabhāratī: laya/kaum... knowledge)", ["Rasa"], [], "residue: camatkara"),
 ("NAT-SANTA9", "Natya", "NŚ · śānta-navama", T, "santa-rasa-navama (Abhinava)",
  "Peace as ninth rasa (Abhinava vs Daṇḍin-tradition debate)", ["Rasa"], [], ""),
]

VNODES = [
 ("arg-sds-carvaka", "SDS", [], "Cārvāka doxography: pratyakṣa-only, element-consciousness, no ātman/paraloka", "Vada", "Pratitantra"),
]
VEDGES = [
 ("e27", "arg-sds-carvaka", "arg-sv-atman", "khandana", "Viruddha", "SDS", "dehatmavada (Carvaka ch.)", 0.7),
 ("e28", "arg-sv-atman", "arg-sds-carvaka", "uddhara", "Badhita", "SV", "atman reply to dehatmavada", 0.65),
]


def main():
    old = json.loads((ROOT / "data" / "sutras.json").read_text(encoding="utf-8"))
    by_id = {r["id"]: r for r in old}
    added = 0
    for rec in R:
        rec = list(rec) + ["", "", ""]
        rid, text, not_, tier, san, tr = rec[0], rec[1], rec[2], rec[3], rec[4], rec[5]
        pada = rec[6] if isinstance(rec[6], list) else []
        pram = rec[7] if isinstance(rec[7], list) else []
        logic = rec[8] if isinstance(rec[8], str) else ""
        if rid not in by_id:
            p = provenance(tier, f"{not_} (canon-4)")
            by_id[rid] = {"id": rid, "textId": text, "adhyaNotation": not_,
                          "sanskrit": normalize_iast(san), "translation": tr,
                          "padarthasMentioned": pada, "pramanasInvoked": pram,
                          **({"logicalForm": logic} if logic else {}),
                          "confidence": p["tier"], "sourceNote": p["note"],
                          "verifyAgainst": "NS/YS/DhvA/Natya/SDS eds."}
            added += 1
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
    print(f"sutras {len(old)} -> {len(out)} (+{added}); nodes {len(nodes)}; edges {len(edges)}")


if __name__ == "__main__":
    main()

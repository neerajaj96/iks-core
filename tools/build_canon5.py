"""Canon round 5: Arthasangraha (Mimamsa praxis), Sribhasya/Tattvasankhyana
(Vedanta schools), Nyayabindu, Syadvadamanjari, Yuktibhasa series records;
+5 texts; JS procedural terms; +4 inferences; vada +1/+3 (orphan wiring).
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.ingest import provenance, normalize_iast, write_json, mirror_to_docs

ROOT = Path(__file__).resolve().parents[1]
V, F, T = "verbatim", "famous-gist", "topic-digest"

NEWTEXTS = [
 {"id": "ASang", "titleSanskrit": "Arthasaṅgraha", "titleEnglish": "Compendium of Meanings (Laugakshi Bhaskara)",
  "authorIds": ["laugakshi"], "layer": "prakarana", "darsana": "Purva-Mimamsa", "corpusRefs": {}},
 {"id": "Sribhasya", "titleSanskrit": "Śrībhāṣya", "titleEnglish": "Radiant Commentary on Brahma Sutras (Ramanuja)",
  "authorIds": ["ramanuja"], "layer": "bhashya", "rootTextId": "BS", "darsana": "Visistadvaita", "corpusRefs": {}},
 {"id": "TattvaSank", "titleSanskrit": "Tattvasaṅkhyāna", "titleEnglish": "Enumeration of Realities (Madhva)",
  "authorIds": ["madhva"], "layer": "prakarana", "darsana": "Dvaita", "corpusRefs": {}},
 {"id": "NBindu", "titleSanskrit": "Nyāyabindu", "titleEnglish": "Drop of Logic (Dharmakirti, 3 chapters)",
  "authorIds": ["dharmakirti"], "layer": "prakarana", "darsana": "Bauddha-Yogacara", "corpusRefs": {}},
 {"id": "SyadManj", "titleSanskrit": "Syādvādamañjarī", "titleEnglish": "Blossom of Conditioned Assertion (Mallisena)",
  "authorIds": ["mallisena"], "layer": "tika", "darsana": "Jaina-Svetambara", "corpusRefs": {}},
]

# (id, textId, notation, tier, sanskrit, translation, pada, pram, logic)
R = [
 # ---- Arthasangraha ----
 ("AS-DHARMA", "ASang", "AS · dharma", T, "yagadi-dharma (codana-laksana-anuvada)",
  "Dharma as sacrifice etc., restating Jaimini's injunction-mark", ["Artha"], ["Sabda"], ""),
 ("AS-BHAVANA", "ASang", "AS · bhāvanā-dvaya", F, "sabdi-bhavana / arthi-bhavana",
  "Two productive operations: verbal and objective", ["Artha"], [], ""),
 ("AS-VIDHI4", "ASang", "AS · vidhi-caturvidha", F, "utpatti-viniyoga-prayoga-adhikara-vidhayah",
  "Four injunctions: originative, applicational, performative, entitlement", ["Artha"], ["Sabda"], ""),
 ("AS-MANTRA", "ASang", "AS · mantra", T, "mantra-anuvacana-smaraka",
  "Mantras as remembrancers of the rite-details", ["Sabda"], ["Sabda"], ""),
 ("AS-ARTHAVADA3", "ASang", "AS · arthavāda-trividha", F, "gunavada-anuvada-bhutarthavada",
  "Eulogies threefold: quality-praise, restatement, existent-fact", ["Sabda"], ["Sabda"], ""),
 ("AS-NAMA", "ASang", "AS · nāmadheya", T, "namadheya-vidhi ...",
  "Names enjoin (Mātrāvaruṇa-type analysis)", ["Sabda"], ["Sabda"], ""),
 ("AS-NISEDHA", "ASang", "AS · pratiṣedha", T, "pratisedha-paryudasa",
  "Prohibition vs exclusion: two negative modes", ["Artha"], [], ""),
 ("AS-PRAMANA6", "ASang", "AS · pramāṇa-ṣaṭka", T, "sat-pramanani (anupalabdhi-sahita)",
  "Six pramāṇas restated for the Bhāṭṭa student", ["Pramana"], ["Anupalabdhi"], ""),
 ("AS-APURVA", "ASang", "AS · apūrva", T, "apurva-svarga-hetu",
  "Unseen potency linking rite to heaven", ["Artha"], [], ""),
 # ---- Sribhasya ----
 ("SRI-TATTVA3", "Sribhasya", "Śrībh · tattvatraya", F, "cit-acit-isvara-tattvatrayam",
  "Three realities: sentient, insentient, Lord", ["Tattva"], []),
 ("SRI-SARIRA", "Sribhasya", "Śrībh · śarīraka-brahman", F, "sarira-sariri-bhava-brahma",
  "Brahman qualified by world as its body", ["Artha"], ["Sabda"], ""),
 ("SRI-BHAKTI", "Sribhasya", "Śrībh · bhakti-prapatti", T, "bhakti-prapatti-moksopaya",
  "Devotion and surrender as release-means", ["Artha"], [], ""),
 ("SRI-SAMANVAYA", "Sribhasya", "Śrībh 1.1 · saviśeṣa-samanvaya", T, "savisesa-brahma-samanvaya",
  "Harmony teaches qualified brahman (vs nirviśeṣa)", ["Artha"], ["Sabda"], ""),
 # ---- Tattvasankhyana ----
 ("TSANK-BHEDA5", "TattvaSank", "TSaṅ · pañcabheda", F, "jiva-jiva, jiva-jada, jiva-isvara, jada-jada, jada-isvara",
  "Five eternal differences", ["Tattva"], []),
 ("TSANK-PRAMEYA", "TattvaSank", "TSaṅ · prameya", T, "navadha-prameya ...",
  "Knowables enumerated (Lord foremost)", ["Tattva"], []),
 ("TSANK-VISHNU", "TattvaSank", "TSaṅ · viṣṇu-sārvottama", T, "visnu-sarvottama, laksmi-nitya",
  "Viṣṇu supreme; Lakṣmī ever-free", ["Artha"], ["Sabda"], ""),
 ("TSANK-TARA", "TattvaSank", "TSaṅ · tāratamya", F, "taratamya-mukti ...",
  "Gradation among released souls", ["Artha"], [], ""),
 # ---- Nyayabindu ----
 ("NB-PRAT", "NBindu", "NB 1 · pratyakṣa", F, "kalpanapodham abhrantam pratyaksam",
  "Perception: construction-free, non-errant", ["Pramana"], ["Pratyaksa"], ""),
 ("NB-SVA", "NBindu", "NB 2 · svārthānumāna", T, "trairupya-linga ...",
  "Triple-marked mark-bearer inference restated compactly", ["Pramana"], ["Anumana"], ""),
 ("NB-PARA", "NBindu", "NB 3 · parārthānumāna", T, "paksa-vacana ...",
  "Thesis-statement form for others", ["Pramana"], ["Anumana"], ""),
 # ---- Syadvadamanjari ----
 ("SYM-SYAD", "SyadManj", "SyM · syādvāda-sāra", T, "syadvada-dvatrimsat ...",
  "Thirty-two verses' essence: conditioned assertion", ["Other"], [], "◇_n"),
 ("SYM-SAPTA", "SyadManj", "SyM · saptabhaṅgī", T, "saptabhangi-sloka ...",
  "Sevenfold predication versified", ["Other"], [], ""),
 ("SYM-NAYA7", "SyadManj", "SyM · sapta-naya", F, "naigama-sangraha-vyavahara-rjusutra-sabda-samabhirudha-evambhuta",
  "Seven standpoints enumerated", ["Pramana"], [], ""),
 ("SYM-ANEKANTA", "SyadManj", "SyM · anekānta-jñāna", T, "anekanta-jnana-pramana",
  "Many-sided cognition as valid knowledge", ["Pramana"], [], ""),
 # ---- Yuktibhasa series ----
 ("YUK-JYA", "YuktiB", "Yuktibhāṣā · jyā-śreṇi", T, "jya-sara-sreni ...",
  "Arc-sine series via iterative correction (upapatti)", ["Other"], []),
 ("YUK-CAPA", "YuktiB", "Yuktibhāṣā · cāpa-pi", T, "capa-samskara-pi ...",
  "Arc correction refining π (3.141592653... target)", ["Other"], []),
]

TERMS = [
 ("atidesa", "अतिदेश", "atideśa", ["Purva-Mimamsa"], ["JS-ADH78"], "Other", "Ati", ""),
 ("viniyoga", "विनियोग", "viniyoga", ["Purva-Mimamsa"], ["AS-VIDHI4"], "Other", "Vin", ""),
 ("prayoga", "प्रयोग", "prayoga", ["Purva-Mimamsa"], ["JS-ADH34"], "Other", "Pra", ""),
 ("tantra", "तन्त्र", "tantra", ["Purva-Mimamsa"], ["JS-ADH1112"], "Other", "Tan", ""),
 ("prasanga", "प्रसङ्ग", "prasaṅga", ["Purva-Mimamsa"], ["JS-ADH1112"], "Other", "Pras", ""),
]

INF = [
 ("inf-tc-kevala", "Nyaya", "Nyaya-5", "ghata", "vacyatva", "prameyatva", "sarva-vastu",
  "kevalanvayi siddhanta-laksana", "none", "Navya form of affirmative-only inference"),
 ("inf-ps-hetu", "Bauddha-Yogacara", "Buddhist-2", "sabda", "anityatva", "krtakatva", "ghata",
  "hetucakra valid pattern", "none", "Hetucakra-sanctioned valid reason"),
 ("inf-js-apurva", "Purva-Mimamsa", "Nyaya-5", "yajamana", "svarga", "apurva", "jyotistoma",
  "bhavana-apurva-phala", "none", "Heaven via unseen potency from rite"),
 ("inf-nk-karya", "Nyaya", "Nyaya-5", "ksiti", "sakrtrkatva", "karyatva", "ghata",
  "NK stavaka-5 form", "none", "Udayana's effect-argument in five members"),
]

VNODES = [
 ("arg-sri-sarira", "Sribhasya", [], "Śarīraka-brahman vs nirviśeṣa: qualified whole (Rāmānuja reply)", "Vada", "Pratitantra"),
]
VEDGES = [
 ("e29", "arg-vp-6pr", "arg-advsiddhi-mithyatva", "samanvaya", "none", "VP", "pramana-paribhasa ally", 0.45),
 ("e30", "arg-sds-idx", "arg-tc-pratyaksa", "samanvaya", "none", "SDS", "Nyaya chapter doxography", 0.4),
 ("e31", "arg-sri-sarira", "arg-advsiddhi-mithyatva", "khandana", "Viruddha", "Sribhasya", "sariraka-vada", 0.7),
]


def main():
    texts = json.loads((ROOT / "data" / "texts.json").read_text(encoding="utf-8"))
    tids = {t["id"] for t in texts}
    for t in NEWTEXTS:
        if t["id"] not in tids:
            texts.append(t)
    write_json(ROOT / "data" / "texts.json", texts)
    mirror_to_docs(ROOT, "texts.json", texts)

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
            p = provenance(tier, f"{not_} (canon-5)")
            by_id[rid] = {"id": rid, "textId": text, "adhyaNotation": not_,
                          "sanskrit": normalize_iast(san), "translation": tr,
                          "padarthasMentioned": pada, "pramanasInvoked": pram,
                          **({"logicalForm": logic} if logic else {}),
                          "confidence": p["tier"], "sourceNote": p["note"],
                          "verifyAgainst": "ASang/Sribhasya/TattvaSank/NB/SyadManj/YuktiB eds."}
            added += 1
    out = sorted(by_id.values(), key=lambda r: (r["textId"], r["adhyaNotation"]))
    write_json(ROOT / "data" / "sutras.json", out)
    mirror_to_docs(ROOT, "sutras.json", out)

    terms = json.loads((ROOT / "data" / "terms.json").read_text(encoding="utf-8"))
    tids2 = {t["id"] for t in terms}
    for i, s, ia, sc, ds, sort, sym, res in TERMS:
        if i not in tids2:
            terms.append({"id": i, "sanskrit": s, "iast": ia, "darsanaScope": sc,
                          "definitionSutras": ds, "ontologicalSort": sort, "formalSymbol": sym,
                          "confidence": "famous-gist", "sourceNote": f"term {ia} (canon-5)",
                          "verifyAgainst": "Monier-Williams + sastra editions",
                          **({"nonFormalizableResidue": res} if res else {})})
    write_json(ROOT / "data" / "terms.json", terms)
    mirror_to_docs(ROOT, "terms.json", terms)

    infs = json.loads((ROOT / "data" / "inferences.json").read_text(encoding="utf-8"))
    iids = {x["id"] for x in infs}
    FULL = {"pakse": True, "sapakse": True, "vipakseAbsent": True}
    TRAIRUPYA = {"Savyabhicara": {"pakse": True, "sapakse": True, "vipakseAbsent": False},
                 "Asiddha": {"pakse": False, "sapakse": False, "vipakseAbsent": True}}
    for i, sc, f, pa, sa, h, d, v, hb, n in INF:
        if i not in iids:
            infs.append({"id": i, "school": sc, "form": f, "paksa": pa, "sadhya": sa,
                         "hetu": h, "drstanta": d, "vyapti": v, "hetvabhasa": hb,
                         "trairupya": dict(TRAIRUPYA.get(hb, FULL)),
                         "members": {}, "note": n, "confidence": "famous-gist",
                         "verifyAgainst": "NS/TC/NK/JS eds."})
    write_json(ROOT / "data" / "inferences.json", infs)
    mirror_to_docs(ROOT, "inferences.json", infs)

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
    print(f"texts {len(texts)}; sutras {len(old)} -> {len(out)} (+{added}); "
          f"terms {len(terms)}; infs {len(infs)}; nodes {len(nodes)}; edges {len(edges)}")


if __name__ == "__main__":
    main()

"""Canon round 3: fills referenced-but-missing texts (TC khandas, Dignaga PS,
Udayana NK, Jaimini JS, Bhasapariccheda BP, Vedantasara, Dandin KAd, Vamana KAS),
+7 texts, vada +3/+3. Honest tiers throughout.
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
 {"id": "PS", "titleSanskrit": "Pramāṇasamuccaya", "titleEnglish": "Compendium of Means of Knowledge (Dignaga)",
  "authorIds": ["dignaga"], "layer": "prakarana", "darsana": "Bauddha-Yogacara",
  "corpusRefs": {"gretil": "Pramanasamuccaya"}},
 {"id": "NK", "titleSanskrit": "Nyāyakusumāñjali", "titleEnglish": "Handful of Flowers of Logic (Udayana, 5 stavakas)",
  "authorIds": ["udayana"], "layer": "prakarana", "darsana": "Nyaya", "corpusRefs": {}},
 {"id": "JS", "titleSanskrit": "Mīmāṃsāsūtra", "titleEnglish": "Mimamsa Sutras (Jaimini, 12 adhyayas)",
  "authorIds": ["jaimini"], "layer": "sutra", "darsana": "Purva-Mimamsa",
  "corpusRefs": {"gretil": "Mimamsasutra"}},
 {"id": "BP", "titleSanskrit": "Bhāṣāpariccheda (Kārikāvalī)", "titleEnglish": "Division of Categories (Visvanatha + Muktavali)",
  "authorIds": ["visvanatha"], "layer": "prakarana", "darsana": "Nyaya", "corpusRefs": {}},
 {"id": "VedSara", "titleSanskrit": "Vedāntasāra", "titleEnglish": "Essence of Vedanta (Sadananda)",
  "authorIds": ["sadananda"], "layer": "prakarana", "darsana": "Advaita", "corpusRefs": {}},
 {"id": "KAd", "titleSanskrit": "Kāvyādarśa", "titleEnglish": "Mirror of Poetry (Dandin)",
  "authorIds": ["dandin"], "layer": "prakarana", "darsana": "Sahitya", "corpusRefs": {}},
 {"id": "KAS", "titleSanskrit": "Kāvyālaṅkārasūtra", "titleEnglish": "Aphorisms on Poetics (Vamana: riti)",
  "authorIds": ["vamana"], "layer": "sutra", "darsana": "Sahitya", "corpusRefs": {}},
]

# (id, textId, notation, tier, sanskrit, translation, pada, pram, logic)
R = [
 # ---- Tattvacintamani 4 khandas ----
 ("TC-NIR", "TC", "TC Pratyakṣa · nirvikalpaka", F, "nirvikalpakam nama ...",
  "Non-qualificative perception admitted (vs Buddhist perception-only + Mīmāṃsā)", ["Pramana"], ["Pratyaksa"], ""),
 ("TC-SAV", "TC", "TC Pratyakṣa · savikalpaka", T, "savikalpaka-visista-jnana",
  "Qualificative perception as full-fledged pramā; yokanup... structure", ["Pramana"], ["Pratyaksa"], ""),
 ("TC-ANYA", "TC", "TC Pratyakṣa · anyathākhyāti", F, "anyathakhyati-bhrama",
  "Error as misattribution (vs ātma/asat/ākhyāti rivals)", ["Pramana"], ["Pratyaksa"], ""),
 ("TC-VYAP5", "TC", "TC Anumāna · vyāpti-pañcaka", F, "vyapti-pancaka ...",
  "Five successive vyāpti definitions filtering avyāpti/ativyāpti/asambhava", ["Pramana"], ["Anumana"], "H ⇉[ladder] S"),
 ("TC-VYAP-SIDDH", "TC", "TC Anumāna · siddhānta-lakṣaṇa", T, "hetutavacchedaka-sambandhena ...",
  "Final definition: hetu-limiter-relation bearing the sādhya", ["Pramana"], ["Anumana"], "H ⇉[A_H→A_S] S"),
 ("TC-KEVALA", "TC", "TC Anumāna · kevalānvayin", F, "kevalanvayi (vacyo ghatah prameyatvat)",
  "Affirmative-only concomitance; no vipakṣa exists", ["Pramana"], ["Anumana"], ""),
 ("TC-KEVALA-VYAT", "TC", "TC Anumāna · kevalavyatirekin", T, "kevalavyatireki (prthivi ...)",
  "Negative-only concomitance via difference from the rest", ["Pramana"], ["Anumana"], ""),
 ("TC-UPAMANA", "TC", "TC Upamāna · short khaṇḍa", T, "upamana-samarthana (gavaya)",
  "Comparison defended as independent pramā in one compact khaṇḍa", ["Pramana"], ["Upamana"], ""),
 ("TC-SABDA", "TC", "TC Śabda · vidhi/arthavāda", T, "sabda-khanda (vidhi, mantra, namadheya)",
  "Verbal cognition: injunction, eulogy, names; Mīmāṃsā/Buddhist replies", ["Pramana"], ["Sabda"], ""),
 ("TC-ISVARA", "TC", "TC · īśvara-anumāna", T, "ksityadi-karyatva ...",
  "Īśvara inferred from effect-hood (Kusumāñjali lineage absorbed)", ["Artha"], ["Anumana"], ""),
 # ---- Dignaga ----
 ("PS-TRAI", "PS", "PS 2 · trairūpya", F, "trairupya-hetu (paksadharmata, sapakse, vipakse-asattva)",
  "Triple-marked reason; Hetucakra's 9-fold table, only 2 valid", ["Pramana"], ["Anumana"], "H(a) ∧ (H⇉S)"),
 ("PS-HETU9", "PS", "PS · hetucakra", F, "navavidha-hetu (2 sadhana, 7 dusana)",
  "Nine reason-patterns across sapakṣa/vipakṣa presence", ["Pramana"], ["Anumana"], ""),
 ("PS-PRAT", "PS", "PS 1 · pratyakṣa", F, "kalpanapodha (svalaksana-visaya)",
  "Perception free of construction; unique particular as object", ["Pramana"], ["Pratyaksa"], ""),
 ("PS-SVA-PARA", "PS", "PS · svārtha/parārtha", T, "svathanumana-parathanumana",
  "Inference for oneself (parāmarśa) vs for others (statement)", ["Pramana"], ["Anumana"], ""),
 ("PS-APOHA", "PS", "PS 5 · apoha", T, "anyapoha-sabda",
  "Exclusion theory of meaning (matured by Dharmakīrti)", ["Sabda"], [], ""),
 # ---- Udayana ----
 ("NK-1", "NK", "NK stavaka 1 · maṅgala", T, "isvara-avasyakatva-upakrama",
  "Opening: why Īśvara must be established (against Mīmāṃsā/Buddhist)", ["Artha"], ["Anumana"], ""),
 ("NK-2", "NK", "NK stavaka 2 · pramāṇa", T, "isvara-pramana-vicara",
  "Which pramāṇas can reach Īśvara (śabda + anumāna alliance)", ["Pramana"], ["Sabda", "Anumana"], ""),
 ("NK-3", "NK", "NK stavaka 3 · ātman", T, "atma-nityatva (vs ksanika)",
  "Permanent self against Buddhist momentariness", ["Tattva"], ["Anumana"], ""),
 ("NK-4", "NK", "NK stavaka 4 · aiśvarya", T, "jnana-iccha-prayatna-guna-isvara",
  "Īśvara's qualities: cognition, desire, effort eternal", ["Artha"], [], ""),
 ("NK-5", "NK", "NK stavaka 5 · navavidha-hetu", F, "karyayojanadhrtyapadeh ... sadhya visvavid avyayah",
  "Nine reasons (effect, conjunction, support...) prove the omniscient maker", ["Artha"], ["Anumana"], "karya->karta"),
 # ---- Jaimini (paired adhyayas) ----
 ("JS-112", "JS", "JS 1.1.2 · dharma-lakṣaṇa", V, "codanalaksano rtho dharmah",
  "Dharma is the injunction-indicated good", ["Artha"], ["Sabda"], "V_Sa iff codana"),
 ("JS-ADH12", "JS", "JS 1-2 · pramāṇa/kratu", T, "pramana-kratu-bheda",
  "Means of knowing dharma; sacrifice typology", ["Pramana"], ["Sabda"], ""),
 ("JS-ADH34", "JS", "JS 3-4 · śeṣa/prayoga", T, "sesa-prayoga",
  "Subsidiaries and performance procedure", ["Artha"], [], ""),
 ("JS-ADH56", "JS", "JS 5-6 · krama/adhikāra", T, "krama-adhikara",
  "Sequence and eligibility (who may sacrifice)", ["Artha"], [], ""),
 ("JS-ADH78", "JS", "JS 7-8 · atideśa/ūha", T, "atidesa-uha",
  "Extended application and ritual modification", ["Artha"], [], ""),
 ("JS-ADH910", "JS", "JS 9-10 · ūha/bādha", T, "uha-badha",
  "Modification details and sublation conflicts", ["Artha"], [], ""),
 ("JS-ADH1112", "JS", "JS 11-12 · tantra/prasaṅga", T, "tantra-prasanga",
  "Combination of rites and concurrent efficacy", ["Artha"], [], ""),
 # ---- Bhasapariccheda ----
 ("BP-PAD", "BP", "BP · padārtha-vibhāga", T, "saptapadarthi-sangraha",
  "Seven categories condensed in verse (dravyaādi)", ["Dravya"], []),
 ("BP-KARANA", "BP", "BP · kāraṇa-traividhya", F, "samavayi-asamavayi-nimitta-karana",
  "Three causes: inherent, non-inherent, efficient", ["Samavaya"], ["Anumana"], "Caus_phi(x->y)"),
 ("BP-GUNA", "BP", "BP · guṇa-catuviṃśati", T, "caturvimsati-guna",
  "Twenty-four qualities surveyed", ["Guna"], []),
 ("BP-PRAMANA", "BP", "BP · pramāṇa-catuṣṭaya", T, "pratyaksadi-catvari",
  "Four pramāṇas in Navya-Nyāya idiom", ["Pramana"], ["Pratyaksa", "Anumana", "Upamana", "Sabda"], ""),
 ("BP-ISVARA", "BP", "BP · īśvara-anumāna", T, "ksiti-karyatva ...",
  "Classroom Īśvara proof from effect-hood", ["Artha"], ["Anumana"], ""),
 ("BP-MANAS", "BP", "BP · mano-'ṇutva", T, "manaso nutvam ...",
  "Mind's atomicity from serial cognition", ["Dravya"], ["Anumana"], ""),
 # ---- Vedantasara ----
 ("VSARA-ANU", "VedSara", "Vedāntasāra · anubandha", F, "adhikari-visaya-sambandha-prayojana",
  "Four preliminaries: student, subject, relation, fruit", ["Artha"], []),
 ("VSARA-ADHY", "VedSara", "Vedāntasāra · adhyāropa/apavāda", F, "adhyaropa-apavada-nyaya",
  "Superimposition and rescission method (snake-rope)", ["Artha"], []),
 ("VSARA-KOSA", "VedSara", "Vedāntasāra · kośa-traya", T, "sarira-traya-panca-kosa",
  "Three bodies, five sheaths; mahāvākya fitness", ["Tattva"], []),
 ("VSARA-SRAV", "VedSara", "Vedāntasāra · śravaṇādi", T, "sravana-manana-nididhyasana",
  "Hearing, reflection, meditation triad", ["Pramana"], ["Sabda"], []),
 ("VSARA-SAMADHI", "VedSara", "Vedāntasāra · samādhi", T, "savikalpa-nirvikalpa-samadhi",
  "Two absorptions; jīvanmukti vs videhamukti", ["Tattva"], []),
 ("VSARA-VAKYA", "VedSara", "Vedāntasāra · mahāvākya-viveka", T, "tattvamasi-bhagatyaga-laksana",
  "Part-abandonment implication in 'that thou art'", ["Artha"], ["Sabda"], ""),
 # ---- Dandin / Vamana ----
 ("KAD-GUNA", "KAd", "Kāvyādarśa 1 · guṇa/alaṅkāra", T, "dasa-guna-marga",
  "Ten excellences; two paths (Vaidarbha/Gauḍa) prefiguring rīti", ["Dhvani"], []),
 ("KAD-DOSA", "KAd", "Kāvyādarśa · doṣa", T, "kavya-dosa (padartha-adi)",
  "Faults of poetry surveyed", ["Dhvani"], []),
 ("KAS-RITI", "KAS", "KĀS 1.2.6 · rīti", V, "ritiratma kavyasya",
  "Style is the soul of poetry (Vāmana vs Dhvani school)", ["Dhvani"], []),
 ("KAS-GUNA", "KAS", "KĀS 3 · guṇa/doṣa", T, "sabda-artha-guna",
  "Twenty excellences (10 verbal + 10 semantic); faults opposed", ["Dhvani"], []),
]

VNODES = [
 ("arg-nk-isvara", "NK", [], "Stavaka 5: nine reasons rescue Īśvara against TS-type critiques", "Vada", "Pratitantra"),
 ("arg-ps-trairupya", "PS", [], "Trairūpya/Hetucakra: two-member form challenges pañcāvayava bulk", "Vada", "Pratitantra"),
 ("arg-js-vidhi", "JS", [], "Codanā-only dharma; apūrva suffices — no Īśvara needed (vs Nyāya)", "Vada", "Sarvatantra"),
]
VEDGES = [
 ("e24", "arg-nk-isvara", "arg-ts-isvara", "uddhara", "Badhita", "NK", "stavaka 5", 0.65),
 ("e25", "arg-ps-trairupya", "arg-tc-vyapti", "purvapaksa", "Asiddha", "PS", "hetucakra", 0.6),
 ("e26", "arg-js-vidhi", "arg-nm-isvara", "khandana", "Satpratipaksa", "JS", "codana-adhikarana", 0.6),
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
            p = provenance(tier, f"{not_} (canon-3)")
            by_id[rid] = {"id": rid, "textId": text, "adhyaNotation": not_,
                          "sanskrit": normalize_iast(san), "translation": tr,
                          "padarthasMentioned": pada, "pramanasInvoked": pram,
                          **({"logicalForm": logic} if logic else {}),
                          "confidence": p["tier"], "sourceNote": p["note"],
                          "verifyAgainst": "TC/PS/NK/JS/BP/VedSara/KAd/KAS eds."}
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
    print(f"texts {len(texts)}; sutras {len(old)} -> {len(out)} (+{added}); "
          f"nodes {len(nodes)}; edges {len(edges)}")


if __name__ == "__main__":
    main()

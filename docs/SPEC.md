# IKS-MAM v1.0 — Formal Specification (Phases 1–5)

This document is the canonical spec snapshot. Full mathematical content lives in the
original design message; this file pins the implementable commitments:

## Phase 1 — Schema
`schema/iks-schema.json` + `src/types.ts`. Units: Text, SutraNode, SastricTerm,
PramanaDef, Inference (Nyaya-5/Buddhist-2/Jaina-Trairupya), ArgumentNode, VadaEdge, Cognition.

## Phase 2 — Ontology
- **2A Poset:** C(1) ⊂ B(2)=V(2) ⊂ S(3)=J(3) ⊂ N(4) ⊂ M/A(6); V_* validators; svataḥ/parataḥ flag.
- **2B Padārthas:** D(9: VS 1.1.5) ⊔ G(24) ⊔ K(5: VS 1.1.7) ⊔ Sāmānya ⊔ Viśeṣa ⊔ Samavāya(1) ⊔ Abhāva; Nyāya-16 (NS 1.1.1) with prameya-12 (NS 1.1.9).
- **2C Tattvas:** 25 DAG, guna simplex s+r+t=1, satkāryavāda (parināma), kaivalya=discriminant.
- **2D Syādvāda:** 7-state standpoint-indexed matrix (asti/nasti/kramena/avaktavya combos), negation table.
- **2E Anumāna:** pañcāvayava (NS 1.1.32) with dṛṣṭānta-existence vs dvaivayava trairūpya; 5 hetvābhāsas.
- **2F Vyākaraṇa:** G=(V,Σ,R,S), vipratiṣedhe paraṃ (A.1.4.2), anuvṛtti inheritance; sphoṭa η:D⇒S colimit.
- **2G Sāhitya:** R=Φ(V,A,Y)⊙S₀, 8 sthāyī→9 rasa; dhvani (Sv,Sl,Svya) dominance classes.

## Phase 3 — IKS-NN operators
A_φ, PR, AN, ⊏_R, ⇉, ¬_p/¬_d/¬_a/≠_id, Π_Q, lāghava rule. Worked: parvato vahnimān (limiters),
bhūtale ghaṭo nāsti, nīlo ghaṭaḥ. See `src/logic/iks_nn.py`.

## Phase 4 — Vāda graph
G=(V,E,W), ~25 seed texts, 7 argument nodes, 6 typed edges incl. Nyāyāmṛta↔Advaitasiddhi dyad,
KKK→TC rebuild, SV→TS, Śatadūṣaṇī. Kathā typing (vāda/jalpa/vitaṇḍā). Prover pipeline:
śābdabodha-tag → IKS-NN → Lean/dependent types → SMT → verdict + residue.

## Phase 5 — Build plan
M0 corpus → M1 ontology → M2 IKS-NN/Lean → M3 anumāna → M4 graph → M5 pilots → M6 release.
Non-formalizable residue (tātparya, adhikāra, anubhava, pratibhā, camatkāra) flagged explicitly.

## Provenance
NS 1.1.1/1.1.3/1.1.4/1.1.32, VS 1.1.5/1.1.7, SK kā.4, TC 4 khaṇḍas, saptabhaṅgī sources.

## v2.0 Addendum (all-workstreams stretch)
- **Corpus:** 7 → 159 sūtras (NS 62, VS 29, SK 20, YS 8, TĀ 8, MMK 6, Vyākaraṇa 10, Vedānta/Mīmāṁsā/Sāhitya/Gaṇita 16); new `terms` (33), `inferences` (30), `cognitions` (12); vāda 7V/6E → 16V/16E; every record `confidence`-tiered; `tools/ingest.py` + `tools/build_*.py` pipeline; `tools/conformance.py` audit in CI.
- **Logic:** Satpratipakṣa detector fixed (counter-reason symmetry), Jaina `construct_jaina`, `vyapti_pañcaka` ladder; syād `evaluate` enforces (p_n1,p_n2) consistency; 40-case adversarial matrix in `tests/test_matrix.py`.
- **Graph/API:** PageRank (dangling-mass correct), kathā filter, weighted degree, fallacy histogram, D3 export; FastAPI routes + `POST /anuman/validate` (+ stdlib parity fallback).
- **Lean (gold):** `lean/lakefile.lean` + pinned toolchain; proved: sorts distinctness, 9-dravya count, abhāvābhāva involution (classical), vyāpti grounding +/- pair, syād-negation involution + fixpoints, hetvābhāsa detector theorems; sphoṭa/rasa kept as documented opaque residue.
- **Gaṇita:** Āryabhaṭa π + 25-sine table, Mādhava series + Yuktibhāṣā correction (correction beats naive at n=50).
- **Evals:** 15 → 38 tests; conformance + docs-sync enforced in CI alongside new `lean` job.
- **Pages:** `docs/` interactive — corpus search (text/confidence filters), SVG vāda graph, hetvābhāsa/rasa live demos.

## v2.1 Addendum (depth stretch)
- **SK complete:** all 70 kārikās as individual records (`SK-K01..70`; verbatim only for exactly-remembered wording, outline-level themes flagged `topic-digest` with edition pointers); thematic clusters retained.
- **Vyākaraṇa 10 → 94:** famous Aṣṭādhyāyī rules across adhyāyas 1–4, 6–8 (saṃjñā, it-markers, kāraka/vibhakti, sandhi, affixation) + Mahābhāṣya/Kaumudī/Vākyapadīya index; corrected `A-LAT` to 3.2.123.
- **Corpus total 313 sūtras;** coverage floor raised to 300 in evals; version 2.1.0.

## v2.2 Addendum (canon-2 stretch)
- **Prasthānatrayī:** 12 Upaniṣad + 7 Gītā selections (verbatim for short famous: īśāvāsyam, satyameva jayate, uttiṣṭhata, prajñānam brahma, karmaṇy-evādhikāraḥ...) + 4 Brahmasūtra-adhyāya records.
- **Buddhist/Jaina indices:** PV 4 chapters + apoha; AKB 8 kośasthānas (new AKB text); TS Nyāya/Sāṅkhya/Mīmāṃsā/Jaina/Īśvara parīkṣās; TĀ +6 adhyāya records.
- **Sāhitya:** Nāṭyaśāstra 6 (new Natya text; rasa-sūtra verbatim) + 5 alaṅkāras incl. KP kāvya-lakṣaṇa verbatim.
- **Gaṇita:** Āryabhaṭīya 5 pādas + kuṭṭaka; BSS zero/negative rules (new BSS text); SSiro Līlāvatī/Bīja (cakravāla)/Gola (new SSiro text).
- **Vyākaraṇa:** full 32-pāda Aṣṭādhyāyī map + 4 famous samāsa/taddhita rules.
- **Vāda 16/16 → 23/23** (PV/AKB/BS/NS/Jaina/Madhyamaka/TS-Īśvara nodes; 7 edges incl. śabda-nityatva Satpratipakṣa).
- **Lean:** trairūpya structure + 3 theorems. **Evals:** shared-ground benchmark suite (every debate edge verified to share ≥ pratyakṣa); 45 tests; floor 400; version 2.2.0.

## v2.3 Addendum (canon-3 stretch)
- **Fills referenced-but-missing texts:** TC 10 khaṇḍa records (nirvikalpaka/anyathākhyāti/vyāpti-pañcaka/siddhānta/kevalin/upamāna/śabda/īśvara), Dignāga PS 5 (trairūpya/hetucakra 9/kalpanāpoḍha), Udayana NK 5 stavakas, Jaimini JS 7 (1.1.2 verbatim + paired adhyāyas), Bhāṣāpariccheda 6, Vedāntasāra 6, Daṇḍin 2, Vāmana 2 (rītirātmā verbatim).
- **Vāda 23/23 → 26/26** (NK→TS-Īśvara uddhāra, PS→TC-vyāpti pūrvapakṣa, JS→NM-Īśvara khaṇḍana).
- **Lean:** +3 theorems (syād fix3, viruddha/bādhita precedence mirroring Python). **Packaging:** CITATION.cff, Dockerfile (CI-built). 461 sūtras, 36 texts, floor 450; version 2.3.0.

## v2.4 Addendum (lexicon stretch)
- **Terms 33 → 60:** Navya-Nyāya apparatus (prakāratā/viśeṣyatā/saṃsargatā/nirūpaka/paryāpti/parāmarśa/pakṣatā), Mīmāṃsā (apūrva/bhāvanā/vidhi/codanā), Vedānta (adhyāsa/māyā/jīva/īśvara/brahman/mokṣa/vivarta), Buddhist (svalakṣaṇa/sāmānyalakṣaṇa/kṣaṇikatva/pratītya/śūnyatā/apoha), Jaina (naya/nikṣepa/kevalajñāna) — all cross-referenced to existing sūtra ids.
- **Inferences 30 → 43:** vidhi/arthāpatti/anupalabdhi variants, kevalānvayin-2, svartha/parārtha Buddhist forms, Jaina-naya, Mīmāṃsā-bhāvanā, +3 adversarial (red-hot-iron anaikāntika, sandal bādhita, audibility viruddha).
- **Cognitions 12 → 20:** nirvikalpaka/savikalpaka, smṛti/saṃśaya/svapna (valid 0 with reason), yogaja, parāmarśa, kevala.
- **Pages:** 4th tab browsing terms/inferences. **Lean §8:** pramāṇa acceptance tables + 5 decide theorems. Floors 55/40/18; version 2.4.0.

## v2.5 Addendum (balance stretch)
- **NS Books 3–5 depth (+12):** ātma-śarīra/indriya/artha parīkṣā, buddhi-anityatva, doṣa/duḥkha/apavarga-svarūpa, jāti/nigraha applications, śāstra-samāpti.
- **Yoga practice (+6):** 1.12/2.46/3.1/3.2 verbatim (abhyāsa, sthirasukham, dhāraṇā, dhyāna) + prāṇāyāma/samādhi.
- **Sāhitya (+8):** Dhvanyāloka 4 udyotas; Nāṭya bhāva-sum/sāttvika/vighna/śānta-navama.
- **Cārvāka enters vāda:** SDS doxography node + khaṇḍana/uddhāra dyad with Ślokavārttika-ātman (27V/28E).
- **API `/stats`** (both branches) + tested; **Pages stats strip**. **Lean:** poset-subset theorems (baudha⊆nyāya⊆mīmāṃsā, cārvāka⊆all). 487 sūtras, floor 480; version 2.5.0.

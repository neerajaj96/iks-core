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

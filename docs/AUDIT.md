# IKS-Core Trust Audit — v2.7 (2026-10-13)

How the corpus was checked, what was wrong, what was fixed. Method: every
Sanskrit wording claim diffed against a primary e-text; every URL HEAD-checked
live; duplicates detected by normalized content-hash. Builders that performed
each step are committed under `tools/` for reproducibility.

## Provenance of this audit's reference editions
- Pāṇini: sanskritdocuments sūtrapāṭha PDF + sortable sūtra index (consolidated
  from sūtrapāṭha + AVG/Sktdocs commentaries), vendored as
  `tools/fixtures/panini_sutrapatha.txt` (3,967 sūtras).
- Sāṅkhya: GRETIL Ruzsa SK TEI (`sa_IzvarakRSNa-sAMkhyakArikA.xml`, CC BY-NC-SA).
- Yoga: GRETIL Yogasūtra TEI (Ānandāśrama ed.).
- Nyāya lists: NS 5.1.1/5.2.1 enumeration tradition (Vātsyāyana/Vidyabhusana);
  e-text diff pending (flagged below).

## Phase 1 — Confirmed error fixes: 2 / 103 verbatim (~2%)
| Record | Was | Verified text | Root cause |
|---|---|---|---|
| A-11162 (1.1.62) | "pratyayaḥ" | "pratyayalope pratyayalakṣaṇam" | confused with 3.1.1 |
| A-2122 (2.1.22) | 1.2.42's text | "tatpuruṣaḥ" | pasted wrong sūtra |

## Phase 2 — Dedup merge: 6 pairs, 15 records → canonical
A-1103/A-1113, A-LAT/A-32123, SK-4/SK-K04, SK-SID/SKK-SAMJNA, SK-K01/SK-1…SK-K57/SK-57
plus 9 old SK singles merged into K-series with content transplant (richer
translations preserved). 3 term refs remapped (SK-17/19→SK-K17/19, SK-3→SK-K03).
New guard: normalized-Sanskrit content-hash uniqueness in `tools/conformance.py`
— corpus now has **0 content duplicates** (caught 3 false-positive pada-maps
during calibration; fixed by keeping digits in the hash).

## Phase 3 — Systematic Pāṇini audit: 83/83 PASS
Fixture-backed word-compare of every comparable `A-*` record.
First run: 61 PASS / 23 FAIL. 12 FAILs were harness artifacts (visarga,
avagraha, anusvāra, geminate print-variants) fixed in the comparator;
**11 were real** and all fixed: 2 mislabeled texts (1.1.52 carried 1.1.65's
text; 1.1.57 carried 1.1.64's), 1 misnumbering (aṇudit… is 1.1.69, not 8.4.68;
record renamed A-11169), 1 wrong-number text (8.4.58 = anusvāra rule),
4 truncated long sūtras filled (3.1.7, 4.1.2, 1.4.52, 2.1.4 gloss stripped),
3 transcription slips (anusvāra m, phantom g in suptiṅantam, -kartrkat).
Final: **83 PASS, 0 FAIL** (1 range-record skipped by design, 1 index-record
unparsable by design). 64 records carry `audited` stamps.

## Phase 4 — SK + Nyāya-list audit
- **27 of 70 SK-K* themes corrected** (~39%; mostly cluster-theme conflations
  in kārikās 27–67, e.g. K29/K35/K48–K51 off-by-one-cluster, K62↔K64 swap),
  each re-anchored to GRETIL SK verse numbers. Famous wordings (k3/k9/k17/
  k40/k57/k64/k68…) confirmed.
- Jāti-24 / nigraha-22 enumerations match NS 5.1.1/5.2.1 tradition —
  0 changes (e-text diff still pending; recorded as residual risk).

## Phase 5 — Live provenance: 40/41 texts, 55 URLs HEAD-checked
Resolution via archive.org metadata API + GRETIL/sanskritdocuments/Wikisource
direct fetches. First-pass lesson: **30/41 hand-guessed archive.org slugs were
dead** — none stored; only live-checked URLs committed. YuktiB flagged
`noStableEtext` (Sarma print edition). `tools/linkcheck.py --check` runs in a
monthly CI workflow (`linkcheck.yml`) against `data/texts.json`.

## Residual risks (explicit, not silent)
1. Undiacriticized IAST by design — macron/retroflex precision out of scope.
2. SK variant readings across editions not adjudicated (GRETIL apparatus noted).
3. Translations and IKS-NN logicalForms are interpretive modeling, unaudited.
4. Jāti/nigraha names checked vs tradition, not yet vs NS e-text.
5. Vāda edge weights remain expert-judgment by design.

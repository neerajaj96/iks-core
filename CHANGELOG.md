# Changelog — IKS-Core (IKS-MAM engine)

Format: Added / Changed / Fixed per release. Corpus counts are sūtra records.

## [2.9.0] — 2026-10-14 — Depth
- Added: scripted full NS-589 + YS-195 + JS-2601 + BS-559 ingestion from vendored
  GRETIL texts (wording verbatim, translations tiered gists, `sameWordingAs`
  links for edition repetitions); 32 thin-text top-ups (VP/SDS/SV/PP/SataD).
  4,357 sūtras.
- Added: translation tiers (53 reviewed / ~450 hand-gist / ~3,800 machine-gist).
- Added: `iks_core/prover/` (IKS-NN parser, Lean exporter, verdict CLI 47/47).
- Changed: `iks_core.*` pip-installable package; py3.10–3.13 CI matrix.
- Added: GHCR publish, Panini/SK audit CI gates, property tests.

## [2.8.0] — NS e-text audit, MMK chapters, Sāṅkhya/Yoga vāda debut
- Fixed NS-1.1.5/1.1.10/1.1.17 wordings vs GRETIL NS; jāti-24/nigraha-22 verified.
- Added MMK 27-chapter clusters; arg-sk-satkarya, arg-ys-citta (+2/+2 vāda).
- Added Pages kathā filter. 504 sūtras, 46 tests.

## [2.7.0] — Trust audit
- Fixed 1.1.62 + 2.1.22 misattributions; merged 15 dup records (content-hash CI guard).
- Pāṇini systematic audit 83/83; 27/70 SK themes corrected; 40/41 texts live URLs.
- Added docs/AUDIT.md, monthly link-check CI. 498 sūtras.

## [2.6.0] — Schools stretch
- Arthasaṅgraha, Śrībhāṣya, Tattvasaṅkhyāna, Nyāyabindu, Syādvādamañjarī (+5 texts);
  vāda 28/31; CITATION.cff; Dockerfile. 513 sūtras.

## [2.5.0] — Balance stretch
- NS Books 3–5 depth; YS practice records; Dhvanyāloka/Nāṭya completion;
  Cārvāka vāda debut; `/stats` endpoint; Lean poset theorems. 487 sūtras.

## [2.4.0] — Lexicon stretch
- 60 terms, 43 inferences, 20 cognitions; Pages lexicon tab; Lean pramāṇa tables.

## [2.3.0] — Canon-3
- TC khaṇḍas, Dignāga, Udayana, Jaimini, Bhāṣāpariccheda, Vedāntasāra (+7 texts).

## [2.2.0] — Canon-2
- Prasthānatrayī, PV/AKB/TS/TA indices, Nāṭya, Gaṇita classics, 32-pāda map.

## [2.1.0] — SK-70 + Vyākaraṇa-94.

## [2.0.0] — Full engine: schema, ontology, IKS-NN, vāda graph, Lean kernel, API.

## [1.0.0] — Initial release: taxonomy schema + pilot engine.

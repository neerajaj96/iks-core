# Changelog — IKS-Core (IKS-MAM engine)

Format: Added / Changed / Fixed per release. Corpus counts are sūtra records.

## [Unreleased] — v2.9.0
- Added: scripted full NS (~589) + YS (195) ingestion from vendored GRETIL texts;
  wording verbatim, translations tiered gists (`translationTier/Source`, `editionRef`).
- Added: translation-tier audit (53 reviewed); Panini + SK audits gated in CI;
  property tests (PageRank stochasticity, syād/detector agreement fuzz, gist invariants).
- Changed: package renamed `src.*` → `iks_core.*`; `pip install -e .` supported + CI-tested.
- Added: GHCR image publish on tags; CHANGELOG, CONTRIBUTING, issue templates, dependabot.

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

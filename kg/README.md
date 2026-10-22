# IKS Knowledge Graph

A source-bound knowledge graph for Indian Knowledge Systems (IKS), with a
complete top-level taxonomy and deep coverage of Vyākaraṇa and the Dhātupāṭha.
Every historical assertion is represented as a reified `iks:Claim` with a
citation, source locator, verification status, and audit metadata.

The generated graph is published at
<https://neerajaj96.github.io/iks-core/kg/>. Generated artifacts are not
committed here; the published files are versioned under `docs/kg/` and the
build outputs remain reproducible from the pinned sources.

## Build

```sh
python -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/python tools/generate_rules.py --check
.venv/bin/python tools/generate_dhatus.py --check
.venv/bin/python -m iks_kg build
.venv/bin/python -m iks_kg validate
.venv/bin/python -m pytest
```

`build` writes `dist/iks-kg.{ttl,nt,jsonld}`, the JSON-LD context, the SHACL
shapes, and reports under `reports/`.

## Source snapshots

The pinned snapshots under `sources/cache/` are excluded from this public
repository because several source texts carry non-commercial,
educational-use, or reference-use terms. Restore them under the filenames and
SHA-256 values in `data/sources.json` before building or running the tests; see
`sources/README.md` and the limitations below.

## Scope

- 4 Vedas, 6 Vedāṅgas, 4 Upavedas, 18 Mahāpurāṇas, and the 18-vidyā and
  14-vidyāsthāna lists.
- 9 broad Darśanas, explicitly labeled as a project taxonomy rather than a
  historical count.
- 64 Kāmasūtra `aṅga-vidyā` items, cross-checked against a second witness
  (TextGrid/Nirṇayasāgara 1900), and the 64 Kāvyamīmāṃsā `upavidyā` count.
- All 3,983 Aṣṭādhyāyī sūtras (adhyāyas 1–8) from the Vidyut sūtrapāṭha, with
  37 Vyākaraṇa terms.
- 2,228 Dhātus covering the complete root corpus with an English gloss
  (27 core + 57 additional + 126 extended + 2,018 outside_common), each
  cross-checked against Vidyut.
- 6,373 typed knowledge entities overall; the `entities` statistic counts only
  top-level taxonomy entities and Kalās.

## Evidence model

Claims use these verification statuses:

- `verified_primary`: directly supported by the cited primary text.
- `verified_secondary`: supported by a scholarly reference or dataset.
- `flagged_uncertain`: a documented uncertainty remains.
- `editorial`: an explicit project-level identification or taxonomy decision.

`unverified_hypothesis` records must not be exported. Each claim has a
citation with either a verified source span (`evidenceQuote`, `spanStart`,
`spanEnd`) or a stable dataset record hash. Source files are pinned by SHA-256
in `data/sources.json`. TSV spans are resolved by row code and normalized row
offsets, not by first string occurrence.

## Data layout

- `schema/iks-kg.ttl`: ontology.
- `schema/iks-kg.shacl.ttl`: validation shapes.
- `schema/context.jsonld`: local JSON-LD context.
- `data/sources.json`: source manifests and licenses.
- `data/texts.json`: text and witness records.
- `data/taxonomy.json`: taxonomy entities and canonical lists.
- `data/kalas.json`: 64 Kāmasūtra items.
- `data/rules.json`: all 3,983 Aṣṭādhyāyī sūtras with exact SLP1 text;
  regenerate with `tools/generate_rules.py [--check]`.
- `data/terms_vyakarana.json`: 37 source-bound Vyākaraṇa terms.
- `data/dhatu_selection.json`: 2,228 roots with core/additional/extended/
  outside_common tiers; regenerate with `tools/generate_dhatus.py [--check]`.
- `sources/cache/`: pinned source snapshots and extracted datasets.

## Known limitations

- The Kāmasūtra 64-item list is at **1.3.15**, not 1.3.16. The GRETIL witness
  prints an empty parenthetical at item 12; the TextGrid/Nirṇayasāgara 1900
  witness reads `udaka-āghātaḥ` with no lacuna, so item 12 is now
  `verified_primary`. The total of 64 is independently confirmed by both
  witnesses.
- Items 62–64 remain `flagged_uncertain`: both witnesses transmit them as
  elliptical genitive plurals dependent on `vidyānāṃ jñānam`, and the second
  witness does not resolve the referent.
- Witness variants are recorded as notes and `textual_crosscheck` claims:
  items 8, 21, 34, 38, 44, 52, 54, and 59 differ between GRETIL and the
  TextGrid/Nirṇayasāgara main text or its Chaukhambha variants.
- The Kāmasūtra calls these items `aṅga-vidyā`, not `kalā`. The term `kalā`
  and the count of 64 upavidyās come from Kāvyamīmāṃsā chapter 2; that source
  is explicitly marked as not proofread.
- The 18 Mahāpurāṇas are the Viṣṇupurāṇa list, not a universal canon.
- The nine Darśanas are a project taxonomy; do not cite the grouping as a
  historical count.
- The full Vidyut sūtrapāṭha is covered, but the original 20-rule pilot was
  the subset cross-checked against audited iks-core records. Full coverage uses
  Vidyut as the source of record. The read-only iks-core Pāṇini fixture
  supplies 3,967 comparisons: 3,801 are exact after normalization, 166 differ
  orthographically or textually, and 16 Vidyut rules are absent from the
  fixture. The fixture is not a build dependency; reproduce with
  `tools/compare_rules.py`.
- The primary Dhātupāṭha dataset has 2,259 rows: 2,229 root records and 30
  gaṇasūtra records. The gaṇasūtras are documented but not modeled as roots.
  Root `09.0029` is a pathabheda variant without an English gloss and is
  excluded, leaving 2,228 roots.
- Root `01.1114` has a genuine Vidyut meaning variant: the primary record reads
  `gatireṣaṇayoḥ`, Vidyut reads `gatiroṣaṇayoḥ`. The primary meaning is
  exported; the Vidyut crosscheck is `flagged_uncertain` with a known-issue
  note.
- Newly added Vyākaraṇa terms are provisional editorial glosses tied to their
  defining sūtra rows; they are not full translations.
- The Muṇḍaka witness carries restrictive educational-use terms; the
  Viṣṇupurāṇa and TextGrid Kāmasūtra snapshots are CC BY-NC-SA 4.0. See
  `data/sources.json` before redistribution.
- Agama/Tantra material is outside the current scope.

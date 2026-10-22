# Changelog

## Unreleased

- Added a static knowledge-graph explorer at
  <https://neerajaj96.github.io/iks-core/kg/explorer.html>.
- Added `tools/build_explorer.py`, deterministic explorer JSON, lazy claim
  loading, deep links, and `tests/test_explorer.py`.
- Extended published-artifact verification and CI to check explorer data
  freshness and consistency.

## 0.1.0 - 2026-10-22

- Added the complete 2,228-root Dhātupāṭha with 210 common roots retaining
  core/additional/extended tiers and 2,018 roots in `outside_common`.
- Added all 3,983 Aṣṭhādhyāyī sūtras and 37 source-bound Vyākaraṇa terms.
- Published 246,010 triples, 8,618 claims, and 6,373 knowledge entities.
- Recorded 4,153 source-span citations and 4,465 record-hash citations.
- Status counts: 6,351 `verified_primary`, 2,258 `verified_secondary`, and 9
  `flagged_uncertain`.
- Added reproducible Dhātupāṭha selection generation and exact TSV row
  anchors.
- Published Turtle, N-Triples, JSON-LD, SHACL, context, coverage, and manifest
  artifacts at <https://neerajaj96.github.io/iks-core/kg/>.
- Added published-artifact verification and CI.

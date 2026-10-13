# Contributing to IKS-Core

## Tier policy (non-negotiable)
- `verbatim`: exact wording, edition-checked. Never write from memory alone.
- `famous-gist`: doctrine certain, wording may vary.
- `topic-digest`: accurate summary; must name the edition to verify against.
- Translations: `reviewed` only after checking a published translation;
  otherwise `translationSource: iks-gist` + `translationTier: topic-digest`.

## Builder discipline
- All corpus changes go through `tools/build_*.py` / `tools/ingest_*.py`
  (idempotent, setdefault-by-id). Never hand-edit `data/*.json`.
- Rerun `python3 tools/conformance.py` and the full pytest suite before pushing.
- New audit tooling lives in `tools/audit_*.py` with vendored fixtures +
  provenance notes; wire gates into `.github/workflows/ci.yml`.

## Corrections
- Open an issue with the record id, the edition evidence (quote + source),
  and the proposed fix. Every fix lands with an `audited` stamp and an
  AUDIT.md entry. See `.github/ISSUE_TEMPLATE/correction.yml`.

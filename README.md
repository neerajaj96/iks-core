# IKS-Core — Indian Knowledge System Mathematical Abstraction Model (IKS-MAM) Engine

Open-source computational engine for Darśana, Vyākaraṇa, Pramāṇa, Vāda, Sāhitya, Gaṇita.

- **Spec:** `docs/SPEC.md` (Phases 1–5 + v2.0 addendum)
- **Schema:** `schema/iks-schema.json` + `src/types.ts`
- **Engine:** `src/ontology/` (pramāṇa poset, padārtha, tattva, syādvāda) · `src/logic/` (IKS-NN operators, anumāna + hetvābhāsa + vyāpti-pañcaka, Jaina trairūpya) · `src/vada/` (debate graph + PageRank/kathā/D3) · `src/vyakarana/` · `src/sahitya/` · `src/ganita/` (Āryabhaṭa + Mādhava upapatti)
- **Formal kernel:** `lean/` (lakefile + toolchain-pinned Lean 4 proofs; `lake build` in `lean/`)
- **API:** `server/api.py` — FastAPI with Swagger (`/docs`) or stdlib fallback; corpus search, graph analytics, `POST /anuman/validate`
- **Corpus:** `data/` (29 texts · 418 sūtras: NS 62, VS 29, SK 90, YS 8, TĀ 14, MMK 12, PV 5, AKB 8, Vyākaraṇa 132, Vedānta/Smṛti 23, Sāhitya 17, Gaṇita 14 · 33 terms · 30 inferences · 12 cognitions · 23+23 vāda) every record provenance-tiered (`verbatim`/`famous-gist`/`topic-digest`); ingest pipeline in `tools/ingest.py`, builders in `tools/build_*.py`; Pages UI in `docs/` (+ `docs/data/` mirrors)

## Quickstart

```bash
python3 -m pytest tests/ -q        # 45 tests (matrix + conformance + shared-ground + api/graph/ganita)
python3 tools/conformance.py       # schema + cross-ref audit
python3 server/api.py              # :8000 (FastAPI if installed, else stdlib)
(cd lean && lake build)            # formal kernel (elan toolchain v4.9.0)
```

## API (FastAPI)

`GET /health /pramana /texts /texts/{id} /sutras?q=&text=&confidence= /sutras/{id} /terms /inferences /cognitions /vada /graph?katha= /graph/export /demo/hill /demo/absence` · `POST /anuman/validate`

## Provenance

Sūtra citations: NS B1–B5 selections, VS padārtha-lakṣaṇas + 9/24/5 enumerations, SK thematic + famous kārikās, YS/TĀ/MMK/Vyākaraṇa/Vedānta/Sāhitya/Gaṇita seeds. Confidence tiers explicit; non-formalizable residue (tātparya, adhikāra, anubhava, pratibhā, camatkāra) flagged, never silently dropped.

## License

MIT — see LICENSE.

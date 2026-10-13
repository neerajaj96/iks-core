# IKS-Core — Indian Knowledge System Mathematical Abstraction Model (IKS-MAM) Engine

Open-source computational engine for Darśana, Vyākaraṇa, Pramāṇa, Vāda, Sāhitya, Gaṇita.

- **Spec:** `docs/SPEC.md` (Phases 1–5 + v2.0 addendum)
- **Schema:** `schema/iks-schema.json` + `src/types.ts`
- **Engine:** `iks_core/ontology/` (pramāṇa poset, padārtha, tattva, syādvāda) · `iks_core/logic/` (IKS-NN operators, anumāna + hetvābhāsa + vyāpti-pañcaka, Jaina trairūpya) · `iks_core/vada/` (debate graph + PageRank/kathā/D3) · `iks_core/vyakarana/` · `iks_core/sahitya/` · `iks_core/ganita/` (Āryabhaṭa + Mādhava upapatti) · `pip install -e .` then `import iks_core`
- **Formal kernel:** `lean/` (lakefile + toolchain-pinned Lean 4 proofs; `lake build` in `lean/`)
- **API:** `server/api.py` — FastAPI with Swagger (`/docs`) or stdlib fallback; corpus search, graph analytics, `POST /anuman/validate`
- **Corpus:** `data/` (41 texts, all link-checked · 1200 sūtras · 65 terms · 47 inferences · 20 cognitions · 30+33 vāda) wording verbatim-from-edition where ingested, translations tiered (`reviewed`/`famous-gist`/`topic-digest`), 97 `audited`; ingest + audit pipeline in `tools/`; Pages UI in `docs/` (+ `docs/data/` mirrors, audit report `docs/AUDIT.md`)

## Quickstart

```bash
python3 -m pytest tests/ -q        # 53 tests (matrix + conformance + shared-ground + properties + api/graph/ganita)
pip install -e .                   # then: import iks_core
python3 tools/conformance.py       # schema + cross-ref + content-hash audit
python3 tools/audit_panini.py --report && python3 tools/audit_sk.py
python3 server/api.py              # :8000 (FastAPI if installed, else stdlib)
docker build -t iks-core .         # containerized API
(cd lean && lake build)            # formal kernel (elan toolchain v4.9.0)
```

## API (FastAPI)

`GET /health /pramana /texts /texts/{id} /sutras?q=&text=&confidence= /sutras/{id} /terms /inferences /cognitions /vada /graph?katha= /graph/export /stats /demo/hill /demo/absence` · `POST /anuman/validate`

## Provenance

Sūtra citations: NS B1–B5 selections, VS padārtha-lakṣaṇas + 9/24/5 enumerations, SK thematic + famous kārikās, YS/TĀ/MMK/Vyākaraṇa/Vedānta/Sāhitya/Gaṇita seeds. Confidence tiers explicit; non-formalizable residue (tātparya, adhikāra, anubhava, pratibhā, camatkāra) flagged, never silently dropped.

## License

MIT — see LICENSE.

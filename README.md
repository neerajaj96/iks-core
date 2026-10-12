# IKS-Core — Indian Knowledge System Mathematical Abstraction Model (IKS-MAM) Engine

Open-source computational engine for Darśana, Vyākaraṇa, Pramāṇa, Vāda, Sāhitya, Gaṇita.

- **Spec:** `docs/SPEC.md` (Phases 1–5: taxonomy schema, set/poset/DAG/matrix ontology, Navya-Nyāya operator library, Vāda-graph + prover architecture, build plan)
- **Schema:** `schema/iks-schema.json` + `src/types.ts`
- **Engine:** `src/ontology/` (pramāṇa poset, padārtha, tattva, syādvāda) · `src/logic/` (IKS-NN operators, anumāna + hetvābhāsa) · `src/vada/` (debate graph) · `src/vyakarana/` · `src/sahitya/`
- **Formal kernel:** `lean/IksNN.lean`
- **API:** `server/api.py` (FastAPI, read-only query layer)
- **Corpus seeds:** `data/*.json` with `corpusRefs` provenance (SARIT/GRETIL/Wikisource)

## Quickstart

```bash
python3 -m pytest tests/ -q        # run competency suite (stdlib only, no install needed)
python3 server/api.py              # serve demo API on :8000 (stdlib http.server fallback)
python3 -c "from src.vada.graph import load_seed; print(load_seed().summary())"
```

## Layout

```
schema/iks-schema.json   JSON Schema (Phase 1)
src/types.ts             TypeScript definitions (Phase 1)
src/ontology/pramana.py  Epistemic accumulation poset + V functions
src/ontology/padartha.py Vaiśeṣika 7 padārthas / Nyāya 16
src/ontology/tattva.py   Sāṅkhya 25-tattva DAG + satkāryavāda
src/ontology/syadvada.py Saptabhaṅgī 7-state matrix
src/logic/iks_nn.py      Navya-Nyāya operators A/PR/AN/¬p¬d¬a≠id/⇒/⊏
src/logic/anumana.py     Pañcāvayava vs dvaivayava + hetvābhāsa detector
src/vada/graph.py        G_Vāda directed knowledge graph
src/vyakarana/panini.py  Aṣṭādhyāyī attribute-grammar pilot + sphoṭa colimit
src/sahitya/rasa.py      Rasa-sūtra vector operator + dhvani layers
data/                    Seed texts, sūtras, vāda nodes/edges
lean/IksNN.lean          Lean 4 formal kernel (sorts, abhāva axioms, vyāpti)
tests/test_all.py        Competency suite
```

## Provenance

Sūtra citations: Vaiśeṣika-Sūtra 1.1.5/1.1.7, Nyāya-Sūtra 1.1.1/1.1.3/1.1.32, Sāṅkhyakārikā, Tattvacintāmaṇi 4 khaṇḍas. Non-formalizable residue (tātparya, adhikāra, anubhava, pratibhā, camatkāra) is explicitly flagged, never silently dropped.

## License

MIT — see LICENSE.

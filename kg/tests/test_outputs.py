import hashlib
import json

from rdflib import Graph

from iks_kg.build import DIST_DIR, write_outputs


def _digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_outputs_are_deterministic_and_valid(built):
    validation = {
        "conforms": built.conforms,
        "results_text": built.results_text,
        "evidence_audit": built.audit,
    }
    write_outputs(built.graph, built.stats, built.coverage, built.audit, validation)
    first = {
        name: _digest(DIST_DIR / name)
        for name in ("iks-kg.nt", "iks-kg.ttl", "iks-kg.jsonld")
    }
    write_outputs(built.graph, built.stats, built.coverage, built.audit, validation)
    second = {
        name: _digest(DIST_DIR / name)
        for name in ("iks-kg.nt", "iks-kg.ttl", "iks-kg.jsonld")
    }
    assert first == second

    parsed = Graph().parse(DIST_DIR / "iks-kg.jsonld", format="json-ld")
    assert set(parsed) == set(built.graph)
    payload = json.loads((DIST_DIR / "iks-kg.jsonld").read_text(encoding="utf-8"))
    ids = [node.get("id") for node in payload["@graph"]]
    assert ids == sorted(ids)

from rdflib import Graph

from iks_kg.build import SCHEMA_DIR


def test_shacl_conforms(built):
    assert built.conforms, built.results_text[:5000]


def test_jsonld_roundtrip(built):
    import json

    context = json.loads((SCHEMA_DIR / "context.jsonld").read_text(encoding="utf-8"))
    data = built.graph.serialize(
        format="json-ld",
        context=context.get("@context", context),
    )
    roundtrip = Graph().parse(data=data, format="json-ld")
    assert len(roundtrip) == len(built.graph)
    assert set(roundtrip) == set(built.graph)

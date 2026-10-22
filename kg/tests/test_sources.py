import csv

from rdflib import Namespace, RDF

from iks_kg.build import _load_json
from iks_kg.sources import SOURCE_DIR, load_sources, witness_text

IKS = Namespace("urn:iks:")


def test_source_manifest():
    sources = load_sources()
    assert len(sources) == 10
    for source in sources.values():
        assert len(source.sha256) == 64
        assert source.license
        assert source.retrieved_at
        assert source.local_path


def test_texts_have_witness_claims(built):
    graph = built.graph
    texts = _load_json("texts.json")["texts"]
    assert len(texts) == 7
    for text in texts:
        node = IKS[text["id"]]
        witnesses = set(graph.objects(node, IKS.hasWitness))
        assert len(witnesses) == len(text["witness_source_ids"])
        assert all(str(w).rsplit(":", 1)[-1] in text["witness_source_ids"] for w in witnesses)


def test_rules_and_terms():
    payload = _load_json("rules.json")
    rules = payload["rules"]
    terms = _load_json("terms_vyakarana.json")["terms"]
    assert len(rules) == 3983
    assert payload["selection"]["total"] == 3983
    assert payload["selection"]["source_sutra_count"] == 3983
    assert len(terms) == 37
    assert len({r["number"] for r in rules}) == 3983
    assert len({t["id"] for t in terms}) == 37

    with (SOURCE_DIR / "sutrapatha-vidyut.tsv").open(encoding="utf-8") as handle:
        source = {row["code"]: row["text"] for row in csv.DictReader(handle, delimiter="\t")}
    assert set(source) == {rule["number"] for rule in rules}
    assert all(rule["slp1"] == source[rule["number"]] for rule in rules)

    by_id = {rule["id"]: rule for rule in rules}
    term_ids = {term["id"] for term in terms}
    for rule in rules:
        assert set(rule.get("relevant_terms", [])) <= term_ids
    for term in terms:
        assert term["claim"]["target"] in by_id
        assert term["id"] in by_id[term["claim"]["target"]].get("relevant_terms", [])


def test_textgrid_markup_is_stripped_for_matching():
    text = witness_text("src-kamasutra-textgrid")
    assert "chvānavetra" not in text
    assert "p32" not in text
    assert "paṭṭikāvetravānavikalpāḥ" in text
    assert "catuḥṣaṣṭiraṅgavidyāḥ" in text


def test_sources_are_typed(built):
    graph = built.graph
    assert len(set(graph.subjects(RDF.type, IKS.Source))) == 10
    assert IKS["src-kamasutra-textgrid"] in set(graph.subjects(RDF.type, IKS.Source))

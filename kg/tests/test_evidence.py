import re

from rdflib import Literal, Namespace, RDF
from rdflib.namespace import SKOS

from iks_kg.sources import find_tsv_row_span, load_sources, witness_text

IKS = Namespace("urn:iks:")


def _count_claims(graph, list_id):
    return set(graph.objects(IKS[list_id], IKS.hasCountClaim))


def _claims_by_source(graph, entity, source_id):
    claims = graph.objects(entity, IKS.hasClaim)
    return [
        c
        for c in claims
        if str(graph.value(graph.value(c, IKS.citation), IKS.source)).rsplit(":", 1)[-1]
        == source_id
    ]


def test_all_span_quotes_match_source(built):
    graph = built.graph
    sources = load_sources()
    checked = 0
    for citation in graph.subjects(RDF.type, IKS.Citation):
        quote = graph.value(citation, IKS.evidenceQuote)
        start = graph.value(citation, IKS.spanStart)
        end = graph.value(citation, IKS.spanEnd)
        if start is None:
            continue
        source_id = str(graph.value(citation, IKS.source)).rsplit(":", 1)[-1]
        text = witness_text(source_id)
        assert text[int(start):int(end)] == str(quote)
        assert sources[source_id].sha256 == str(graph.value(citation, IKS.sourceSha256))
        checked += 1
    assert checked == built.audit["span_citations"]


def test_record_hash_citations(built):
    graph = built.graph
    sources = load_sources()
    checked = 0
    for citation in graph.subjects(RDF.type, IKS.Citation):
        record_hash = graph.value(citation, IKS.recordHash)
        if record_hash is None:
            continue
        assert re.fullmatch(r"[0-9a-f]{64}", str(record_hash))
        source_id = str(graph.value(citation, IKS.source)).rsplit(":", 1)[-1]
        assert sources[source_id].sha256 == str(graph.value(citation, IKS.sourceSha256))
        checked += 1
    assert checked == built.audit["record_hash_citations"]


def test_rule_spans_match_their_tsv_rows(built):
    graph = built.graph
    rules = set(graph.subjects(RDF.type, IKS.Rule))
    assert len(rules) == 3983
    for rule in rules:
        number = str(graph.value(rule, IKS.ruleNumber))
        claim = graph.value(rule, IKS.hasClaim)
        citation = graph.value(claim, IKS.citation)
        start, end, quote = find_tsv_row_span("src-vidyut-sutrapatha", number)
        assert (int(graph.value(citation, IKS.spanStart)), int(graph.value(citation, IKS.spanEnd))) == (start, end)
        assert str(graph.value(citation, IKS.evidenceQuote)) == quote
        assert str(graph.value(claim, IKS.verificationStatus)) == "verified_primary"


def test_term_spans_match_their_defining_rule_rows(built):
    graph = built.graph
    for term in graph.subjects(RDF.type, IKS.VyakaranaTerm):
        claim = graph.value(term, IKS.hasClaim)
        rule = graph.value(term, IKS.definedBy)
        number = str(graph.value(rule, IKS.ruleNumber))
        citation = graph.value(claim, IKS.citation)
        start, end, quote = find_tsv_row_span("src-vidyut-sutrapatha", number)
        assert (int(graph.value(citation, IKS.spanStart)), int(graph.value(citation, IKS.spanEnd))) == (start, end)
        assert str(graph.value(citation, IKS.evidenceQuote)) == quote


def test_kamasutra_list_locator_is_1_3_15(built):
    graph = built.graph
    claims = _count_claims(graph, "list-64-kala")
    assert len(claims) == 2
    for claim in claims:
        locator = str(graph.value(graph.value(claim, IKS.citation), IKS.locator))
        assert "1.3.15" in locator
        assert "1.3.16" not in locator
    assert (IKS["kala-04"], SKOS.prefLabel, Literal("ālekhyam", lang="sa-Latn")) in graph
    assert (IKS["kala-11"], SKOS.prefLabel, Literal("udaka-vādyam", lang="sa-Latn")) in graph
    assert (IKS["kala-12"], SKOS.prefLabel, Literal("udakāghātaḥ", lang="sa-Latn")) in graph


def test_flagged_items_have_known_issue(built):
    graph = built.graph
    for ordinal in (62, 63, 64):
        entity = IKS[f"kala-{ordinal:02d}"]
        flagged = [
            c
            for c in graph.objects(entity, IKS.hasClaim)
            if str(graph.value(c, IKS.verificationStatus)) == "flagged_uncertain"
        ]
        assert len(flagged) == 1
        assert graph.value(flagged[0], IKS.knownIssue) is not None
    assert not [
        c
        for c in graph.objects(IKS["kala-12"], IKS.hasClaim)
        if str(graph.value(c, IKS.verificationStatus)) == "flagged_uncertain"
    ]
    item12 = _claims_by_source(graph, IKS["kala-12"], "src-kamasutra-gretil")
    assert len(item12) == 1
    assert str(graph.value(item12[0], IKS.verificationStatus)) == "verified_primary"


def test_kala_spans_are_inside_the_source_list(built):
    graph = built.graph
    text = witness_text("src-kamasutra-gretil")
    start = text.find("gītam")
    end = text.find("catuḥṣaṣṭiraṅgavidyā")
    assert 0 <= start < end
    for ordinal in range(1, 65):
        entity = IKS[f"kala-{ordinal:02d}"]
        claims = _claims_by_source(graph, entity, "src-kamasutra-gretil")
        assert len(claims) == 1
        citation = graph.value(claims[0], IKS.citation)
        span_start = int(graph.value(citation, IKS.spanStart))
        span_end = int(graph.value(citation, IKS.spanEnd))
        assert start <= span_start < span_end <= end


def test_textgrid_kala_spans_are_inside_the_source_list(built):
    graph = built.graph
    text = witness_text("src-kamasutra-textgrid")
    start = text.find("gītaṃ")
    end = text.find("catuḥṣaṣṭiraṅgavidyāḥ")
    assert 0 <= start < end
    crosschecks = 0
    for ordinal in range(1, 65):
        entity = IKS[f"kala-{ordinal:02d}"]
        for claim in _claims_by_source(graph, entity, "src-kamasutra-textgrid"):
            assert str(graph.value(claim, IKS.assertionType)) == "textual_crosscheck"
            citation = graph.value(claim, IKS.citation)
            span_start = int(graph.value(citation, IKS.spanStart))
            span_end = int(graph.value(citation, IKS.spanEnd))
            assert start <= span_start < span_end <= end
            crosschecks += 1
    assert crosschecks == 12


def test_purana_spans_are_inside_the_source_list(built):
    graph = built.graph
    text = witness_text("src-vp-gretil")
    start = text.find("aṣṭādaśapurāṇānipurāṇajñāḥpracakṣate")
    assert start >= 0
    for member in graph.objects(IKS["list-18-mahapurana"], IKS.hasMember):
        citation = graph.value(graph.value(member, IKS.hasClaim), IKS.citation)
        span_start = int(graph.value(citation, IKS.spanStart))
        assert span_start >= start


def test_count_quotes(built):
    graph = built.graph
    quotes = {}
    for claim in _count_claims(graph, "list-64-kala"):
        assert int(graph.value(claim, IKS.object)) == 64
        citation = graph.value(claim, IKS.citation)
        source = str(graph.value(citation, IKS.source)).rsplit(":", 1)[-1]
        quotes[source] = str(graph.value(citation, IKS.evidenceQuote))
    assert quotes == {
        "src-kamasutra-gretil": "catuḥṣaṣṭiraṅgavidyā",
        "src-kamasutra-textgrid": "catuḥṣaṣṭiraṅgavidyāḥ",
    }

    claim = graph.value(IKS["list-18-vidya"], IKS.hasCountClaim)
    citation = graph.value(claim, IKS.citation)
    assert str(graph.value(citation, IKS.evidenceQuote)) == "vidyahyaṣṭādaśaivatāḥ"
    assert int(graph.value(claim, IKS.object)) == 18

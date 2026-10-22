from rdflib import Namespace, RDF

IKS = Namespace("urn:iks:")

ALLOWED_STATUSES = {
    "verified_primary",
    "verified_secondary",
    "flagged_uncertain",
    "editorial",
}


def test_core_counts(built):
    assert built.stats["entities"] == 109
    assert built.stats["knowledge_entities"] == 6373
    assert built.stats["dhatus"] == 2228
    assert built.stats["rules"] == 3983
    assert built.stats["terms"] == 37
    assert built.stats["texts"] == 7
    assert built.stats["lists"] == 9
    assert built.stats["canonical_lists"] == 8
    assert built.stats["claims"] == built.stats["citations"] == 8618
    assert built.stats["triples"] == 246010


def test_gana_counts(built):
    expected = {
        str(i): n
        for i, n in {
            1: 1156,
            2: 76,
            3: 26,
            4: 161,
            5: 38,
            6: 174,
            7: 25,
            8: 10,
            9: 70,
            10: 492,
        }.items()
    }
    assert built.stats["dhatu_gana_counts"] == expected
    assert sum(expected.values()) == 2228


def test_claims_are_cited_and_sourced(built):
    graph = built.graph
    claims = set(graph.subjects(RDF.type, IKS.Claim))
    assert len(claims) == built.stats["claims"]
    for claim in claims:
        citations = list(graph.objects(claim, IKS.citation))
        assert len(citations) == 1
        citation = citations[0]
        assert graph.value(citation, RDF.type) == IKS.Citation
        assert graph.value(citation, IKS.source) is not None
        assert graph.value(citation, IKS.sourceSha256) is not None
        assert graph.value(citation, IKS.locator) is not None
        assert graph.value(citation, IKS.retrievedAt) is not None


def test_status_policy(built):
    graph = built.graph
    statuses = {str(s) for s in graph.objects(None, IKS.verificationStatus)}
    assert statuses <= ALLOWED_STATUSES
    assert "unverified_hypothesis" not in statuses
    assert built.stats["status_counts"] == {
        "flagged_uncertain": 9,
        "verified_primary": 6351,
        "verified_secondary": 2258,
    }


def test_no_evidence_audit_problems(built):
    assert built.audit["problems"] == []
    assert built.audit["bad_status_claims"] == []
    assert built.audit["claims"] == built.stats["claims"]
    assert built.audit["citations"] == built.stats["citations"]
    assert built.audit["span_citations"] == 4153
    assert built.audit["record_hash_citations"] == 4465

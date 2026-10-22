import json
from collections import Counter
from pathlib import Path

from rdflib import Namespace, RDF

from iks_kg.build import _load_json

IKS = Namespace("urn:iks:")
CACHE = Path(__file__).resolve().parents[1] / "sources" / "cache"


def test_selection_matches_graph(built):
    selection = _load_json("dhatu_selection.json")
    codes = [r["baseindex"] for r in selection["roots"]]
    assert len(codes) == 2228
    assert len(set(codes)) == 2228
    assert codes.count("07.0013") == 1
    assert codes.count("07.0017") == 1
    assert "09.0029" not in codes
    tiers = Counter(r["tier"] for r in selection["roots"])
    assert tiers == {
        "core": 27,
        "additional": 57,
        "extended": 126,
        "outside_common": 2018,
    }
    assert built.coverage["dhatu_selection_total"] == 2228
    assert built.coverage["dhatu_tiers"] == {
        "additional": 57,
        "core": 27,
        "extended": 126,
        "outside_common": 2018,
    }

    graph = built.graph
    assert len(set(graph.subjects(RDF.type, IKS.Dhatu))) == 2228
    for code in codes:
        node = IKS[f"dhatu-{code.replace('.', '-')}"]
        assert str(graph.value(node, IKS.dhatupathaCode)) == code
        assert str(graph.value(node, IKS.crosscheckCode)) == code
        assert graph.value(node, IKS.crosscheckSource) == IKS["src-vidyut-dhatupatha"]


def test_selection_is_complete_root_corpus():
    selection = _load_json("dhatu_selection.json")
    codes = {r["baseindex"] for r in selection["roots"]}
    records = json.loads((CACHE / "dhatu-ashtadhyayi.json").read_text(encoding="utf-8"))
    roots = [
        r
        for r in records["data"]
        if "ganasutra" not in r.get("tags", "").split(",")
    ]
    with_english = {
        r["baseindex"] for r in roots if r.get("artha_english", "").strip()
    }
    missing_english = {
        r["baseindex"] for r in roots if not r.get("artha_english", "").strip()
    }
    assert missing_english == {"09.0029"}
    assert len(records["data"]) == 2259
    assert len(roots) == 2229
    assert codes == with_english
    assert len(codes) == 2228


def test_crosscheck_variant_is_flagged(built):
    graph = built.graph
    node = IKS["dhatu-01-1114"]
    claims = list(graph.objects(node, IKS.hasClaim))
    assert len(claims) == 2
    by_type = {
        str(graph.value(c, IKS.assertionType)): c for c in claims
    }
    primary = by_type["lexical_attestation"]
    crosscheck = by_type["dataset_crosscheck"]
    assert str(graph.value(primary, IKS.verificationStatus)) == "verified_primary"
    assert str(graph.value(crosscheck, IKS.verificationStatus)) == "flagged_uncertain"
    issue = str(graph.value(crosscheck, IKS.knownIssue))
    assert "gatireṣaṇayoḥ" in issue
    assert "gatiroṣaṇayoḥ" in issue
    assert "gatiroṣaṇayoḥ" in str(graph.value(crosscheck, IKS.claimText))


def test_all_ganas_present(built):
    graph = built.graph
    ganas = {int(v) for v in graph.objects(None, IKS.gana)}
    assert ganas == set(range(1, 11))
    assert all(1 <= g <= 10 for g in ganas)


def test_each_dhatu_has_two_attestations(built):
    graph = built.graph
    for node in graph.subjects(RDF.type, IKS.Dhatu):
        types = {
            str(graph.value(c, IKS.assertionType))
            for c in graph.objects(node, IKS.hasClaim)
        }
        assert types == {"lexical_attestation", "dataset_crosscheck"}, node

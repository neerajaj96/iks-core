from rdflib import Namespace

IKS = Namespace("urn:iks:")


def test_list_counts(built):
    graph = built.graph
    expected = {
        "list-4-veda": 4,
        "list-6-vedanga": 6,
        "list-4-upaveda": 4,
        "list-18-vidya": 18,
        "list-14-vidyasthana": 14,
        "list-18-mahapurana": 18,
        "list-64-upavidya": 64,
        "list-64-kala": 64,
    }
    for list_id, count in expected.items():
        assert int(graph.value(IKS[list_id], IKS.memberCount)) == count
        assert graph.value(IKS[list_id], IKS.hasCountClaim) is not None


def test_membership_edges(built):
    graph = built.graph
    for list_id, count in {
        "list-4-veda": 4,
        "list-6-vedanga": 6,
        "list-4-upaveda": 4,
        "list-18-mahapurana": 18,
        "list-64-kala": 64,
        "list-9-darsana": 9,
    }.items():
        members = list(graph.objects(IKS[list_id], IKS.hasMember))
        assert len(members) == count, list_id
        assert len(set(members)) == count, list_id


def test_composite_lists(built):
    graph = built.graph
    vidya_components = list(graph.objects(IKS["list-18-vidya"], IKS.component))
    vidyasthana_components = list(graph.objects(IKS["list-14-vidyasthana"], IKS.component))
    assert sum(int(graph.value(c, IKS.componentCount)) for c in vidya_components) == 18
    assert sum(int(graph.value(c, IKS.componentCount)) for c in vidyasthana_components) == 14


def test_related_64_lists(built):
    graph = built.graph
    kala = IKS["list-64-kala"]
    upavidya = IKS["list-64-upavidya"]
    assert graph.value(kala, IKS.relatedList) == upavidya
    assert graph.value(kala, IKS.sameCountAs) == upavidya
    assert graph.value(kala, IKS.correspondsTo) == upavidya

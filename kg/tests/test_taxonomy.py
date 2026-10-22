from rdflib import Namespace, RDF

from iks_kg.build import _load_json

IKS = Namespace("urn:iks:")


def test_taxonomy_json_shape():
    data = _load_json("taxonomy.json")
    assert len(data["entities"]) == 45
    assert len(data["lists"]) == 8
    ids = [e["id"] for e in data["entities"]]
    assert len(ids) == len(set(ids))


def test_entity_type_counts(built):
    graph = built.graph

    def count(t):
        return len(set(graph.subjects(RDF.type, IKS[t])))

    assert count("Veda") == 4
    assert count("Vedanga") == 6
    assert count("Upaveda") == 4
    assert count("Darsana") == 9
    assert count("Purana") == 18
    assert count("Kala") == 64


def test_darsana_group_is_editorial(built):
    graph = built.graph
    node = IKS["list-9-darsana"]
    assert graph.value(node, IKS.scopeNote) is not None
    assert len(set(graph.objects(node, IKS.hasMember))) == 9


def test_all_puranas_in_list(built):
    graph = built.graph
    members = set(graph.objects(IKS["list-18-mahapurana"], IKS.hasMember))
    assert len(members) == 18
    assert all(str(m).startswith("urn:iks:purana-") for m in members)

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "docs" / "kg" / "data"
BUILDER = ROOT / "kg" / "tools" / "build_explorer.py"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def test_meta_matches_published_graph():
    meta = load("meta.json")
    assert meta["version"] == "0.1.0"
    assert meta["release"]["tag"] == "kg-v0.1.0"
    assert meta["counts"] == {
        "triples": 246010,
        "claims": 8618,
        "citations": 8618,
        "dhatus": 2228,
        "rules": 3983,
        "terms": 37,
        "knowledge_entities": 6373,
        "explorer_claims": 8476,
    }
    assert meta["tiers"] == {
        "additional": 57,
        "core": 27,
        "extended": 126,
        "outside_common": 2018,
    }
    assert sum(meta["ganas"].values()) == 2228
    assert sum(meta["padas"].values()) == 2228


def test_explorer_entity_rows():
    dhatus = load("dhatus.json")
    rules = load("rules.json")
    terms = load("terms.json")
    assert len(dhatus) == 2228
    assert len(rules) == 3983
    assert len(terms) == 37
    assert len({row["code"] for row in dhatus}) == 2228
    assert len({row["number"] for row in rules}) == 3983
    assert all(row["root_sa"] and row["root_iast"] for row in dhatus)
    assert all(row["sa"] and row["iast"] for row in rules)
    assert all(row["rule_id"] in {r["id"] for r in rules} for row in terms)


def test_explorer_claims_are_cited():
    dhatus = load("dhatus.json")
    rules = load("rules.json")
    terms = load("terms.json")
    expected = {
        "dhatu-claims.json": {row["id"] for row in dhatus},
        "rule-claims.json": {row["id"] for row in rules},
        "term-claims.json": {row["id"] for row in terms},
    }
    total = 0
    statuses = Counter()
    for name, ids in expected.items():
        claims = load(name)
        assert set(claims) == ids
        for claim in (item for group in claims.values() for item in group):
            total += 1
            statuses[claim["status"]] += 1
            citation = claim["citation"]
            assert citation["source"]
            assert citation["locator"]
            assert citation["span_start"] is not None or citation["record_hash"]
    assert total == 8476
    assert statuses == {
        "flagged_uncertain": 1,
        "verified_primary": 6248,
        "verified_secondary": 2227,
    }


def test_explorer_data_is_current():
    result = subprocess.run(
        [sys.executable, str(BUILDER), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout

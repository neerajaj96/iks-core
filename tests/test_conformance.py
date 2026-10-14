"""Corpus-conformance + coverage floors (mirrors tools/conformance.py as asserts)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


class TestCoverage(unittest.TestCase):
    def test_floors(self):
        self.assertGreaterEqual(len(load("texts.json")), 40)
        self.assertGreaterEqual(len(load("sutras.json")), 4000)  # v2.9: scripted NS/YS/JS/BS ingestion
        self.assertGreaterEqual(len(load("terms.json")), 60)
        self.assertGreaterEqual(len(load("inferences.json")), 45)
        self.assertGreaterEqual(len(load("cognitions.json")), 18)
        self.assertGreaterEqual(len(load("terms.json")), 30)
        self.assertGreaterEqual(len(load("inferences.json")), 30)
        self.assertGreaterEqual(len(load("vada_nodes.json")), 30)
        self.assertGreaterEqual(len(load("vada_edges.json")), 33)
        self.assertGreaterEqual(len(load("cognitions.json")), 12)

    def test_every_sutra_provenanced(self):
        for s in load("sutras.json"):
            self.assertIn(s.get("confidence"), ("verbatim", "famous-gist", "topic-digest"), s.get("id"))
            self.assertTrue(s.get("sourceNote"), s.get("id"))

    def test_cross_refs(self):
        texts = {t["id"] for t in load("texts.json")}
        sutras = {s["id"] for s in load("sutras.json")}
        for s in load("sutras.json"):
            self.assertIn(s["textId"], texts, s["id"])
        for t in load("terms.json"):
            for ds in t["definitionSutras"]:
                self.assertIn(ds, sutras, t["id"])
        nodes = {n["id"] for n in load("vada_nodes.json")}
        for e in load("vada_edges.json"):
            self.assertIn(e["from"], nodes, e["id"])
            self.assertIn(e["to"], nodes, e["id"])
            self.assertTrue(0.0 <= e["weight"] <= 1.0)

    def test_schema_top_level(self):
        schema = json.loads((ROOT / "schema" / "iks-schema.json").read_text())
        for coll in ("texts", "sutras", "terms", "inferences", "arguments", "edges", "cognitions"):
            self.assertIn(coll, schema["properties"], coll)


if __name__ == "__main__":
    unittest.main()

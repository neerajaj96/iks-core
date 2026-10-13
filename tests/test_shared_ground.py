"""Cross-darsana shared-ground benchmarks: the poset meets that make debate possible."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import unittest
from src.ontology.pramana import PRAMANA_SETS, shared_ground, joint_ground, is_subset_chain


class TestSharedGround(unittest.TestCase):
    def test_nyaya_bauddha_meet(self):
        self.assertEqual(shared_ground("Nyaya", "Bauddha"), {"Pratyaksa", "Anumana"})

    def test_nyaya_mimamsa_meet(self):
        self.assertEqual(shared_ground("Nyaya", "Purva-Mimamsa"),
                         {"Pratyaksa", "Anumana", "Upamana", "Sabda"})

    def test_carvaka_meet_is_perception_only(self):
        for school in PRAMANA_SETS:
            self.assertEqual(shared_ground("Carvaka", school), {"Pratyaksa"}, school)

    def test_bauddha_vaisesika_identical(self):
        self.assertEqual(PRAMANA_SETS["Bauddha"], PRAMANA_SETS["Vaisesika"])
        self.assertEqual(len(joint_ground("Bauddha", "Vaisesika", "Nyaya")), 2)

    def test_full_joint_is_perception(self):
        self.assertEqual(joint_ground(*PRAMANA_SETS), {"Pratyaksa"})

    def test_chain_and_counts(self):
        self.assertTrue(is_subset_chain())
        self.assertEqual(len(PRAMANA_SETS["Samkhya"]), 3)
        self.assertEqual(len(PRAMANA_SETS["Jaina"]), 3)
        self.assertIn("Anupalabdhi", PRAMANA_SETS["Advaita"])
        self.assertNotIn("Sabda", PRAMANA_SETS["Bauddha"])

    def test_vada_edges_have_common_ground(self):
        """Every khandana edge's schools share >= perception (else no debate possible)."""
        import json
        edges = json.loads((Path(__file__).resolve().parents[1] / "data" / "vada_edges.json").read_text())
        nodes = {n["id"]: n for n in
                 json.loads((Path(__file__).resolve().parents[1] / "data" / "vada_nodes.json").read_text())}
        texts = {t["id"]: t for t in
                 json.loads((Path(__file__).resolve().parents[1] / "data" / "texts.json").read_text())}
        school_of = {"Carvaka": "Carvaka", "Bauddha-Sautrantika": "Bauddha",
                     "Bauddha-Yogacara": "Bauddha", "Bauddha-Madhyamaka": "Bauddha",
                     "Jaina-Svetambara": "Jaina", "Jaina-Digambara": "Jaina",
                     "Samkhya": "Samkhya", "Yoga": "Yoga", "Nyaya": "Nyaya",
                     "Vaisesika": "Vaisesika", "Purva-Mimamsa": "Purva-Mimamsa",
                     "Advaita": "Advaita", "Visistadvaita": "Advaita", "Dvaita": "Nyaya",
                     "Vyakarana": "Nyaya", "Sahitya": "Nyaya", "Ganitashastra": "Nyaya"}
        for e in edges:
            a = school_of[texts[nodes[e["from"]]["textId"]]["darsana"]]
            b = school_of[texts[nodes[e["to"]]["textId"]]["darsana"]]
            self.assertIn("Pratyaksa", shared_ground(a, b), e["id"])


if __name__ == "__main__":
    unittest.main()

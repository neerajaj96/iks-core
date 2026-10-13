"""Competency suite: covers 528-NS citation shape, 7 padarthas, 25 tattvas,
7 syad-forms, 5-vs-2 anumana, NN operators, vada paths, rasa, panini."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
import unittest

from iks_core.ontology.pramana import (PRAMANA_SETS, V_pratyaksa, V_anumana, V_sabda,
                                  V_arthapatti, V_anupalabdhi, CognitiveState,
                                  shared_ground, is_subset_chain)
from iks_core.ontology.padartha import check_disjointness, inheres, PADARTHAS_7, NYAYA_16, PRAMEYA_12
from iks_core.ontology.tattva import TATTVAS_25, ancestors, guna_simplex, satkaryavada_holds
from iks_core.ontology.syadvada import evaluate, negate, SYAD_NAMES
from iks_core.logic.iks_nn import hill_inference, floor_absence, Limiter, Absence, Vyapti, laghava_check
from iks_core.logic.anumana import Anumana, detect_hetvabhasa
from iks_core.vada.graph import load_seed
from iks_core.vyakarana.panini import derive_bhavati, sphota_colimit
from iks_core.sahitya.rasa import rasa, dhvani_layers


class TestPramana(unittest.TestCase):
    def test_poset_chain(self):
        self.assertTrue(PRAMANA_SETS["Carvaka"] <= PRAMANA_SETS["Bauddha"] <= PRAMANA_SETS["Nyaya"] <= PRAMANA_SETS["Advaita"])
        self.assertTrue(is_subset_chain())
        self.assertEqual(len(PRAMANA_SETS["Nyaya"]), 4)
        self.assertEqual(len(PRAMANA_SETS["Advaita"]), 6)

    def test_shared_ground(self):
        self.assertEqual(shared_ground("Nyaya", "Bauddha"), frozenset({"Pratyaksa", "Anumana"}))

    def test_validation_functions(self):
        st = CognitiveState(locus="parvata")
        self.assertEqual(V_pratyaksa(True, True, True, st), 1)
        self.assertEqual(V_pratyaksa(True, False, True, st), 0)
        self.assertEqual(V_anumana(True, True, True, "none"), 1)
        self.assertEqual(V_anumana(True, True, True, "Viruddha"), 0)
        self.assertEqual(V_sabda(True, st), 1)
        self.assertEqual(V_arthapatti(True, True), 1)
        self.assertEqual(V_anupalabdhi(True, True), 1)


class TestPadartha(unittest.TestCase):
    def test_counts(self):
        self.assertEqual(len(PADARTHAS_7), 7)
        self.assertEqual(len(NYAYA_16), 16)
        self.assertEqual(len(PRAMEYA_12), 12)
        self.assertTrue(check_disjointness())

    def test_inherence(self):
        self.assertTrue(inheres("rupa", "prthivi"))
        self.assertFalse(inheres("gamana", "akasa"))  # niskriya


class TestTattva(unittest.TestCase):
    def test_25(self):
        self.assertEqual(len(TATTVAS_25), 25)

    def test_dag(self):
        self.assertIn("Prakrti-mula", ancestors("mahabhuta-0"))
        self.assertTrue(guna_simplex(0.5, 0.3, 0.2))
        self.assertTrue(satkaryavada_holds("mahabhuta-0"))
        self.assertFalse(satkaryavada_holds("Purusa"))


class TestSyadvada(unittest.TestCase):
    def test_7_members(self):
        self.assertEqual(len(SYAD_NAMES), 7)
        self.assertEqual(evaluate(1, 0, False, "asti-nasti"), 3)
        self.assertEqual(evaluate(0, 0, True, "avaktavya"), 4)
        self.assertEqual(negate(1), 2)
        self.assertEqual(negate(4), 4)


class TestIksNN(unittest.TestCase):
    def test_operators(self):
        self.assertEqual(Limiter("ghatatva", "ghata").render(), "A_ghatatva(ghata)")
        self.assertIn("¬_a", floor_absence())
        v = Vyapti("dhuma", "dhumatva", "vahni", "vahnitva")
        self.assertIn("⇉", v.render())
        hi = hill_inference()
        for k in ("pratijna", "hetu", "udaharana", "upanaya", "nigamana"):
            self.assertIn(k, hi)
        self.assertEqual(laghava_check(["a", "b"], {"b"}), "b")


class TestAnumana(unittest.TestCase):
    def test_nyaya5_needs_drstanta(self):
        a = Anumana("Nyaya", "Nyaya-5", "parvata", "vahni", "dhuma", drstanta="")
        valid, code = a.validate()
        self.assertFalse(valid)
        a2 = Anumana("Nyaya", "Nyaya-5", "parvata", "vahni", "dhuma",
                     drstanta="mahanasa", vyapti="yatra dhuma tatra vahni")
        m = a2.construct_nyaya5()
        self.assertEqual(len(m), 5)
        self.assertTrue(a2.trairupya(True, True, True))
        self.assertEqual(a2.validate(), (True, "none"))

    def test_buddhist2(self):
        b = Anumana("Bauddha", "Buddhist-2", "parvata", "vahni", "dhuma",
                    vyapti="sapaksa+vipaksa")
        self.assertEqual(len(b.construct_buddhist2()), 2)
        self.assertEqual(detect_hetvabhasa(True, True, True, False, False), "Savyabhicara")
        self.assertEqual(detect_hetvabhasa(True, False, False, True, False), "Viruddha")
        self.assertEqual(detect_hetvabhasa(False, False, False, False, False), "Asiddha")


class TestVada(unittest.TestCase):
    def test_seed_graph(self):
        g = load_seed()
        self.assertGreaterEqual(len(g.nodes), 7)
        self.assertGreaterEqual(len(g.edges), 6)
        paths = g.attack_paths("arg-satadusani", "arg-nyayamrta-mithyatva")
        self.assertTrue(any(len(p) >= 2 for p in paths))


class TestPilots(unittest.TestCase):
    def test_panini(self):
        steps = derive_bhavati()
        self.assertTrue(any("bhavati" in s for s in steps))
        c = sphota_colimit(["bha-va-ti/fast", "bha-va-ti/slow"])
        self.assertEqual(c["sphota"], "S_vākya(bhavati)")

    def test_rasa(self):
        r = rasa(0.8, 0.7, 20.0, "rati")
        self.assertEqual(r["rasa"], "srngara")
        self.assertIn("uttama", dhvani_layers("v", "l", "vy", 0.9, 0.2))

    def test_schema_json_valid(self):
        p = Path(__file__).resolve().parents[1] / "schema" / "iks-schema.json"
        schema = json.loads(p.read_text(encoding="utf-8"))
        self.assertIn("definitions", schema)


if __name__ == "__main__":
    unittest.main()

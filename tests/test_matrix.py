"""Adversarial hetvabhasa matrix + Jaina/trairupya + vyapti-pancaka + syad consistency."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import unittest
from iks_core.logic.anumana import Anumana, detect_hetvabhasa
from iks_core.ontology.syadvada import evaluate


class TestHetvabhasaMatrix(unittest.TestCase):
    def test_all_five_detected(self):
        self.assertEqual(detect_hetvabhasa(True, True, True, False, False), "Savyabhicara")
        self.assertEqual(detect_hetvabhasa(True, False, False, True, False), "Viruddha")
        self.assertEqual(detect_hetvabhasa(True, True, False, False, False, counter_reason=True), "Satpratipaksa")
        self.assertEqual(detect_hetvabhasa(False, False, False, False, False), "Asiddha")
        self.assertEqual(detect_hetvabhasa(True, True, False, False, True), "Badhita")
        self.assertEqual(detect_hetvabhasa(True, True, False, False, False), "none")

    def test_counter_needs_sapakse(self):
        # counter-reason without sapakse support is not Satpratipaksa
        self.assertEqual(detect_hetvabhasa(True, False, False, False, False, counter_reason=True), "none")

    def test_precedence_asiddha_first(self):
        self.assertEqual(detect_hetvabhasa(False, True, True, True, True, True), "Asiddha")

    def test_precedence_viruddha_before_badhita(self):
        self.assertEqual(detect_hetvabhasa(True, True, True, True, True), "Viruddha")

    def test_seed_inferences_reproduce_labels(self):
        """Each hetvabhasa-labeled seed replays its characteristic detector inputs."""
        import json
        from iks_core.logic.anumana import detect_hetvabhasa as det
        replay = {
            "Savyabhicara": {"sapakse": True, "vipakse_present": True},
            "Viruddha": {"contradicts_sadhya": True},
            "Satpratipaksa": {"sapakse": True, "counter_reason": True},
            "Asiddha": {"paksadharmata": False},
            "Badhita": {"defeated": True},
        }
        base = {"paksadharmata": True, "sapakse": True, "vipakse_present": False,
                "contradicts_sadhya": False, "defeated": False, "counter_reason": False}
        infs = json.loads((Path(__file__).resolve().parents[1] / "data" / "inferences.json").read_text())
        for i in infs:
            kw = dict(base)
            kw.update(replay.get(i["hetvabhasa"], {}))
            got = det(kw["paksadharmata"], kw["sapakse"], kw["vipakse_present"],
                      kw["contradicts_sadhya"], kw["defeated"], kw["counter_reason"])
            self.assertEqual(got, i["hetvabhasa"], i["id"])


class TestAnumanaForms(unittest.TestCase):
    def test_jaina_constructor(self):
        a = Anumana("Jaina", "Jaina-Trairupya", "ghata", "asti", "upalabdhi")
        m = a.construct_jaina("syad-asti")
        self.assertIn("syad-asti", m["paksadharmata"])
        self.assertIn("avaktavya", m["avaktavya_rule"])

    def test_vyapti_pancaka_ladder(self):
        ladder = Anumana.vyapti_pancaka()
        self.assertEqual(len(ladder), 5)
        self.assertIn("siddhanta", ladder[-1])

    def test_nyaya5_grounds_vyapti(self):
        a = Anumana("Nyaya", "Nyaya-5", "parvata", "vahni", "dhuma", drstanta="mahanasa")
        self.assertTrue(a.validate()[0])
        b = Anumana("Nyaya", "Nyaya-5", "parvata", "vahni", "dhuma", drstanta="")
        self.assertEqual(b.validate(), (False, "Asiddha"))


class TestSyadConsistency(unittest.TestCase):
    def test_all_seven_members(self):
        self.assertEqual(evaluate(1, 0, False, "asti"), 1)
        self.assertEqual(evaluate(1, 0, False, "nasti"), 2)
        self.assertEqual(evaluate(1, 0, False, "asti-nasti"), 3)
        self.assertEqual(evaluate(1, 0, True, "avaktavya"), 4)
        self.assertEqual(evaluate(1, 0, True, "asti-avaktavya"), 5)
        self.assertEqual(evaluate(1, 0, True, "nasti-avaktavya"), 6)
        self.assertEqual(evaluate(1, 0, True, "asti-nasti-avaktavya"), 7)

    def test_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            evaluate(0, 0, False, "asti")
        with self.assertRaises(ValueError):
            evaluate(1, 1, False, "nasti")
        with self.assertRaises(ValueError):
            evaluate(1, 0, False, "avaktavya")


if __name__ == "__main__":
    unittest.main()

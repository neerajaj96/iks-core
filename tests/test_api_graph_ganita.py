"""API helpers + graph analytics + ganita pilot."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import math
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server"))
from api import search_sutras, validate_anumana, stats  # noqa: E402
from iks_core.vada.graph import load_seed  # noqa: E402
from iks_core.ganita.aryabhata import (aryabhata_pi, aryabhata_sine_table,  # noqa: E402
                                  madhava_pi_series, madhava_correction, yukti_summary)


class TestAPI(unittest.TestCase):
    def test_search(self):
        self.assertGreaterEqual(len(search_sutras(q="pramana")), 3)
        self.assertGreaterEqual(len(search_sutras(text="NS")), 50)
        self.assertGreaterEqual(len(search_sutras(confidence="verbatim")), 5)
        hill = search_sutras(q="vahnimān")
        self.assertTrue(isinstance(hill, list))

    def test_validate_endpoint_logic(self):
        ok = validate_anumana({"paksadharmata": True, "sapakse": True, "form": "Nyaya-5",
                               "drstanta": "mahanasa"})
        self.assertTrue(ok["valid"] and ok["grounded"])
        bad = validate_anumana({"paksadharmata": True, "sapakse": True, "form": "Nyaya-5",
                                "drstanta": ""})
        self.assertEqual(bad["hetvabhasa"], "Asiddha")
        sat = validate_anumana({"paksadharmata": True, "sapakse": True, "counter_reason": True,
                                "form": "Buddhist-2", "drstanta": "x"})
        self.assertEqual(sat["hetvabhasa"], "Satpratipaksa")

    def test_stats(self):
        st = stats()
        self.assertGreaterEqual(st["sutras"], 4000)
        self.assertGreaterEqual(st["texts"], 34)
        self.assertGreaterEqual(st["vada_nodes"], 27)
        self.assertGreaterEqual(st["vada_edges"], 28)
        self.assertIn("verbatim", st["sutras_by_confidence"])
        self.assertEqual(sum(st["sutras_by_confidence"].values()), st["sutras"])


class TestGraphAnalytics(unittest.TestCase):
    def test_pagerank_sums_to_one(self):
        g = load_seed()
        pr = g.pagerank()
        self.assertEqual(len(pr), len(g.nodes))
        self.assertAlmostEqual(sum(pr.values()), 1.0, places=4)

    def test_katha_filter(self):
        g = load_seed().filter_by_katha("Vitanda")
        self.assertGreaterEqual(len(g.nodes), 2)
        for attrs in g.nodes.values():
            self.assertEqual(attrs.get("katha"), "Vitanda")

    def test_d3_export_shape(self):
        d3 = load_seed().d3_export()
        self.assertGreaterEqual(len(d3["nodes"]), 16)
        self.assertGreaterEqual(len(d3["links"]), 16)
        self.assertEqual(len(d3["nodes"]), len(load_seed().nodes))
        self.assertTrue(all("source" in L and "target" in L for L in d3["links"]))

    def test_fallacy_histogram(self):
        h = load_seed().fallacy_histogram()
        self.assertGreaterEqual(h.get("none", 0), 1)
        self.assertIn("Satpratipaksa", h)


class TestGanita(unittest.TestCase):
    def test_aryabhata_pi(self):
        self.assertAlmostEqual(aryabhata_pi(), 3.1416, places=4)
        self.assertLess(abs(aryabhata_pi() - math.pi), 1e-3)

    def test_sine_table(self):
        t = aryabhata_sine_table()
        self.assertEqual(len(t), 25)
        self.assertEqual(t[0], 0)
        self.assertEqual(t[-1], 3438)
        self.assertTrue(all(b >= a for a, b in zip(t, t[1:])))

    def test_madhava_converges(self):
        approx = madhava_pi_series(5000)
        self.assertLess(abs(approx - math.pi), 1e-3)
        corrected = madhava_correction(50)
        naive = madhava_pi_series(50)
        self.assertLess(abs(corrected - math.pi), abs(naive - math.pi))
        self.assertIn("upapatti", yukti_summary()["method"])


if __name__ == "__main__":
    unittest.main()

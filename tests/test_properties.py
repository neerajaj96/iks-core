"""Property-style invariants: randomized + exhaustive agreement checks (stdlib only)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import itertools
import json
import random
import unittest

from iks_core.vada.graph import VadaGraph
from iks_core.ontology.syadvada import evaluate, negate
from iks_core.logic.anumana import detect_hetvabhasa
from server.api import validate_anumana  # noqa: E402  (adds server/ to path itself)


class TestPagerankProperties(unittest.TestCase):
    def test_random_graphs_stochastic(self):
        rng = random.Random(20261013)
        for trial in range(10):
            g = VadaGraph()
            n = rng.randint(2, 12)
            ids = [f"v{i}" for i in range(n)]
            for i in ids:
                g.add_node(i, katha="Vada")
            for _ in range(rng.randint(0, 2 * n)):
                g.add_edge(rng.choice(ids), rng.choice(ids), "khandana",
                           weight=round(rng.random(), 2))
            pr = g.pagerank()
            self.assertEqual(set(pr), set(ids))
            self.assertAlmostEqual(sum(pr.values()), 1.0, places=4)
            self.assertTrue(all(v >= 0.0 for v in pr.values()))

    def test_empty_graph(self):
        self.assertEqual(VadaGraph().pagerank(), {})


class TestSyadProperties(unittest.TestCase):
    def test_negate_is_involution_and_matches_lean_table(self):
        lean_table = {1: 2, 2: 1, 3: 3, 4: 4, 5: 6, 6: 5, 7: 7}
        for m in range(1, 8):
            self.assertEqual(negate(negate(m)), m)
            self.assertEqual(negate(m), lean_table[m])

    def test_evaluate_valid_modes(self):
        good = {(1, 0, False, "asti"): 1, (1, 0, False, "nasti"): 2,
                (1, 0, False, "asti-nasti"): 3, (1, 0, True, "avaktavya"): 4,
                (1, 0, True, "asti-avaktavya"): 5, (1, 0, True, "nasti-avaktavya"): 6,
                (1, 0, True, "asti-nasti-avaktavya"): 7}
        for args, want in good.items():
            self.assertEqual(evaluate(*args), want)

    def test_evaluate_rejects_inconsistent(self):
        modes = ["asti", "nasti", "asti-nasti", "avaktavya", "asti-avaktavya",
                 "nasti-avaktavya", "asti-nasti-avaktavya"]
        rejected = 0
        for p1, p2, sim, mode in itertools.product((0, 1), (0, 1), (False, True), modes):
            needs1 = mode in ("asti", "asti-nasti", "asti-avaktavya", "asti-nasti-avaktavya")
            needs0 = mode in ("nasti", "asti-nasti", "nasti-avaktavya", "asti-nasti-avaktavya")
            needsu = "avaktavya" in mode
            ok = (p1 == 1 if needs1 else True) and (p2 == 0 if needs0 else True) and (sim == needsu)
            if not ok:
                with self.assertRaises(ValueError):
                    evaluate(p1, p2, sim, mode)
                rejected += 1
        self.assertGreater(rejected, 20)


class TestDetectorAgreement(unittest.TestCase):
    def test_validate_matches_detector_all_combos(self):
        count = 0
        for flags in itertools.product((False, True), repeat=6):
            pak, sap, vip, con, defe, ctr = flags
            body = {"paksadharmata": pak, "sapakse": sap, "vipakse_present": vip,
                    "contradicts_sadhya": con, "defeated": defe, "counter_reason": ctr,
                    "form": "Buddhist-2", "drstanta": "x"}
            out = validate_anumana(body)
            direct = detect_hetvabhasa(pak, sap, vip, con, defe, ctr)
            self.assertEqual(out["hetvabhasa"], direct)
            self.assertEqual(out["valid"], direct == "none")
            count += 1
        self.assertEqual(count, 64)


class TestGistInvariants(unittest.TestCase):
    def test_every_gist_record_complete(self):
        data = json.loads((Path(__file__).resolve().parents[1] / "data" / "sutras.json").read_text())
        gist = [r for r in data if r.get("translationSource") == "iks-gist"]
        self.assertGreater(len(gist), 500)
        for r in gist:
            self.assertTrue(r.get("sanskrit"), r["id"])
            self.assertTrue(r.get("translation"), r["id"])
            self.assertTrue(r.get("editionRef"), r["id"])
            self.assertEqual(r.get("translationTier"), "topic-digest")


if __name__ == "__main__":
    unittest.main()

"""Prover: parser coverage, exporter golden output, verdict matrix over seeds."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
import tempfile
import unittest

from iks_core.prover.parser import parse, is_logic, walk
from iks_core.prover.exporter import export_inference, export_all
from iks_core.prover.verdict import verdict
from iks_core.logic.iks_nn import hill_inference, floor_absence

ROOT = Path(__file__).resolve().parents[1]


def kinds(node):
    return {x.kind for x in walk(node)}


class TestParser(unittest.TestCase):
    def test_corpus_forms_never_raise(self):
        forms = sorted(set(r["logicalForm"] for r in
                           json.loads((ROOT / "data" / "sutras.json").read_text())
                           if r.get("logicalForm")))
        extra = list(hill_inference().values()) + [floor_absence()]
        for s in forms + extra:
            n = parse(s)  # must not raise
            self.assertTrue(n.kind)
        self.assertGreaterEqual(len(forms), 40)

    def test_logic_structures(self):
        self.assertIn("Vyapti", kinds(parse("H ⇉[A_H→A_S] S")))
        self.assertIn("Vyapti", kinds(parse("H ⇉ S")))
        self.assertIn("Forall", kinds(parse("∀x(H→P)")))
        self.assertIn("Therefore", kinds(parse("∴P(a)")))
        self.assertIn("Eq", kinds(parse("V_An=0 via viruddha")))
        self.assertIn("Subset", kinds(parse("y ⊆_sakti Prakrti")))
        self.assertIn("MutualAbsence", kinds(parse("x ≠_id y")))
        self.assertIn("Absence", kinds(parse("¬_a^[samyoga,ghatatva] ghata")))
        five = parse("P(a); H(a); ∀x(H→P); H(a)&vyapti; ∴P(a)")
        self.assertEqual(five.kind, "Seq")
        self.assertIn("Func", kinds(five))

    def test_garbage_is_opaque(self):
        self.assertEqual(parse("((").kind, "Opaque")
        self.assertEqual(parse("").kind, "Opaque")


class TestExporter(unittest.TestCase):
    def test_hill_golden(self):
        rec = {"id": "inf-hill-valid", "form": "Nyaya-5", "hetvabhasa": "none"}
        out = export_inference(rec)
        self.assertIn("trairupyaHolds inf_hill_valid_trairupya = true", out)
        self.assertIn("detectHetvabhasa true true false false false false = none", out)

    def test_fallacy_golden(self):
        rec = {"id": "inf-viruddha", "form": "Nyaya-5", "hetvabhasa": "Viruddha"}
        out = export_inference(rec)
        self.assertIn("= (some .viruddha)", out)

    def test_all_records_export(self):
        recs = json.loads((ROOT / "data" / "inferences.json").read_text())
        out = export_all(recs)
        self.assertIn("import IksNN", out)
        self.assertEqual(out.count("theorem"), 2 * len(recs))
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "All.lean"
            p.write_text(out, encoding="utf-8")
            self.assertTrue(p.exists())


class TestVerdictMatrix(unittest.TestCase):
    def test_all_seeds_match_labels(self):
        recs = json.loads((ROOT / "data" / "inferences.json").read_text())
        bad = []
        for r in recs:
            o = verdict(r)
            if not o["match"] or not o["trairupya_agree"] or not o["grounded"]:
                bad.append((r["id"], o))
        self.assertEqual(bad, [])

    def test_known_cases(self):
        recs = {r["id"]: r for r in
                json.loads((ROOT / "data" / "inferences.json").read_text())}
        self.assertTrue(verdict(recs["inf-hill-valid"])["valid"])
        self.assertEqual(verdict(recs["inf-viruddha"])["hetvabhasa"], "Viruddha")
        self.assertEqual(verdict(recs["inf-satprati"])["hetvabhasa"], "Satpratipaksa")
        self.assertEqual(verdict(recs["inf-asiddha"])["hetvabhasa"], "Asiddha")


if __name__ == "__main__":
    unittest.main()

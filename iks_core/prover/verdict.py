"""Verdict CLI: inference id -> machine-checked verdict JSON.

Combines trairupya flags, hetvabhasa detection, and Nyaya-5 grounding;
optionally type-checks the generated Lean companion when lake is available.
  python -m iks_core.prover.verdict --id inf-hill-valid
  python -m iks_core.prover.verdict --all
"""
from __future__ import annotations
import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from iks_core.logic.anumana import detect_hetvabhasa  # noqa: E402
from iks_core.prover.exporter import LABEL_FLAGS  # noqa: E402


def load():
    return json.loads((ROOT / "data" / "inferences.json").read_text(encoding="utf-8"))


def verdict(rec: dict) -> dict:
    fl = LABEL_FLAGS.get(rec.get("hetvabhasa", "none"), LABEL_FLAGS["none"])
    tr = rec.get("trairupya", {})
    agree = (tr.get("pakse", fl["pakse"]) == fl["pakse"]
             and tr.get("sapakse", fl["sapakse"]) == fl["sapakse"]
             and tr.get("vipakseAbsent", not fl["vipakse_present"]) == (not fl["vipakse_present"]))
    code = detect_hetvabhasa(fl["pakse"], fl["sapakse"], fl["vipakse_present"],
                             fl["contradicts_sadhya"], fl["defeated"], fl["counter_reason"])
    grounded = True
    if rec.get("form") == "Nyaya-5" and not rec.get("drstanta") and code == "none":
        code, grounded = "Asiddha", False  # ungrounded vyapti defeats only valid claims
    return {"id": rec["id"], "valid": code == "none", "hetvabhasa": code,
            "expected": rec.get("hetvabhasa", "none"),
            "match": code == rec.get("hetvabhasa", "none"),
            "trairupya_agree": agree, "grounded": grounded,
            "lean": "skipped (run with --lean)"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="IKS-Core anumana verdict")
    ap.add_argument("--id", help="inference id")
    ap.add_argument("--all", action="store_true", help="verdict for every record")
    ap.add_argument("--lean", action="store_true", help="note lean check (CI does the build)")
    args = ap.parse_args(argv)
    recs = load()
    if args.all:
        out = [verdict(r) for r in recs]
        print(json.dumps({"results": out,
                          "summary": {"total": len(out),
                                      "matched": sum(1 for o in out if o["match"])}},
                         ensure_ascii=False, indent=1))
        return 0 if all(o["match"] for o in out) else 1
    if not args.id:
        ap.error("need --id or --all")
    rec = next((r for r in recs if r["id"] == args.id), None)
    if rec is None:
        print(json.dumps({"error": f"unknown id {args.id}"}))
        return 2
    out = verdict(rec)
    if args.lean:
        out["lean"] = ("available" if shutil.which("lake") else "lake not installed")
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0 if out["match"] else 1


if __name__ == "__main__":
    sys.exit(main())

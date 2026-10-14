"""Emit lean/generated/All.lean from data/inferences.json (CI: then lake env lean checks it)."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import json

from iks_core.prover.exporter import export_all

out = ROOT / "lean" / "generated" / "All.lean"
out.parent.mkdir(parents=True, exist_ok=True)
recs = json.loads((ROOT / "data" / "inferences.json").read_text(encoding="utf-8"))
out.write_text(export_all(recs), encoding="utf-8")
print(f"wrote {out} ({len(recs)} inferences)")

#!/usr/bin/env python3
"""Compare selected Vidyut rules with the read-only iks-core Pāṇini fixture.

This is an optional audit helper, not a build input. It reports exact matches
after transliteration and whitespace normalization, plus mismatches and
missing rules.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from iks_kg.translit import normalize_iast, to_iast

ROOT = Path(__file__).resolve().parents[1]
TSV_PATH = ROOT / "sources" / "cache" / "sutrapatha-vidyut.tsv"
DEFAULT_FIXTURE = Path("/root/iks-core/tools/fixtures/panini_sutrapatha.txt")


def _load_vidyut() -> dict[str, str]:
    with TSV_PATH.open(encoding="utf-8") as handle:
        return {row["code"]: row["text"] for row in csv.DictReader(handle, delimiter="\t")}


def _load_fixture(path: Path) -> dict[str, str]:
    rules: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        left, right = line.split("\t", 1)
        rules[left.removeprefix("A ").strip()] = right.strip()
    return rules


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    args = parser.parse_args()

    vidyut = _load_vidyut()
    fixture = _load_fixture(args.fixture)
    selected = sorted(
        vidyut,
        key=lambda code: tuple(int(part) for part in code.split(".")),
    )
    missing = [code for code in selected if code not in fixture]
    mismatches = []
    for code in selected:
        if code not in fixture:
            continue
        left = normalize_iast(to_iast(vidyut[code], "SLP1"))
        right = normalize_iast(to_iast(fixture[code], "Devanagari"))
        if left != right:
            mismatches.append(
                {"number": code, "vidyut": left, "fixture": right}
            )
    print(
        json.dumps(
            {
                "fixture": str(args.fixture),
                "selected": len(selected),
                "present": len(selected) - len(missing),
                "exact": len(selected) - len(missing) - len(mismatches),
                "mismatches": mismatches,
                "missing": missing,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

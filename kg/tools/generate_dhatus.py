#!/usr/bin/env python3
"""Regenerate data/dhatu_selection.json from the pinned Dhātupāṭha data.

The selection covers all root records with an English gloss, excluding the
gaṇasūtra rows. Existing tier assignments are preserved and new roots are
placed in the ``outside_common`` tier. Use --check to verify that the committed
file is current.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

from iks_kg.translit import normalize_iast, to_iast

ROOT = Path(__file__).resolve().parents[1]
SELECTION_PATH = ROOT / "data" / "dhatu_selection.json"
PRIMARY_PATH = ROOT / "sources" / "cache" / "dhatu-ashtadhyayi.json"
CROSSCHECK_PATH = ROOT / "sources" / "cache" / "dhatupatha-vidyut.tsv"
PRIMARY_SOURCE_ID = "src-ashtadhyayi-dhatu"
CROSSCHECK_SOURCE_ID = "src-vidyut-dhatupatha"
TIER_ORDER = ("core", "additional", "extended", "outside_common")


def _code_key(code: str) -> tuple[int, ...]:
    return tuple(int(part) for part in code.split("."))


def _meaning_iast(value: str, script: str) -> str:
    return to_iast(value, script)


def _load_crosscheck() -> dict[str, dict[str, str]]:
    with CROSSCHECK_PATH.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    crosscheck = {row["code"]: row for row in rows}
    if len(crosscheck) != len(rows):
        raise SystemExit("duplicate codes in Vidyut dhātupāṭha TSV")
    return crosscheck


def generate() -> dict[str, Any]:
    existing_payload = json.loads(SELECTION_PATH.read_text(encoding="utf-8"))
    existing_tiers = {
        item["baseindex"]: item["tier"] for item in existing_payload["roots"]
    }
    for code, tier in existing_tiers.items():
        if tier not in TIER_ORDER:
            raise SystemExit(f"unknown existing tier {tier!r} for {code}")

    payload = json.loads(PRIMARY_PATH.read_text(encoding="utf-8"))
    source_rows = payload["data"]
    root_rows = [
        row
        for row in source_rows
        if "ganasutra" not in row.get("tags", "").split(",")
    ]
    ganasutra_rows = [
        row
        for row in source_rows
        if "ganasutra" in row.get("tags", "").split(",")
    ]
    missing_english = [
        row for row in root_rows if not row.get("artha_english", "").strip()
    ]
    selected = [
        row for row in root_rows if row.get("artha_english", "").strip()
    ]
    selected_codes = {row["baseindex"] for row in selected}

    stale_tiers = set(existing_tiers) - selected_codes
    if stale_tiers:
        raise SystemExit(
            f"existing selection code is no longer selectable: {sorted(stale_tiers)[0]}"
        )

    crosscheck = _load_crosscheck()
    roots: list[dict[str, str]] = []
    variants: dict[str, dict[str, str]] = {}
    for row in selected:
        code = row["baseindex"]
        if code not in crosscheck:
            raise SystemExit(f"selected root {code} missing from Vidyut crosscheck")
        if not row.get("dhatu", "").strip():
            raise SystemExit(f"selected root {code} has no root string")
        if not row.get("artha", "").strip():
            raise SystemExit(f"selected root {code} has no Sanskrit meaning")
        if row.get("gana") not in {str(number) for number in range(1, 11)}:
            raise SystemExit(f"selected root {code} has invalid gana")
        if row.get("pada") not in {"P", "A", "U"}:
            raise SystemExit(f"selected root {code} has invalid pada")
        tier = existing_tiers.get(code, "outside_common")
        roots.append({"baseindex": code, "tier": tier})

        primary_meaning = normalize_iast(
            _meaning_iast(row["artha"], "Devanagari")
        )
        vidyut_meaning = normalize_iast(
            _meaning_iast(crosscheck[code]["artha"], "SLP1")
        )
        if primary_meaning != vidyut_meaning:
            primary_iast = _meaning_iast(row["artha"], "Devanagari")
            vidyut_iast = _meaning_iast(crosscheck[code]["artha"], "SLP1")
            variants[code] = {
                "primary_artha": row["artha"],
                "vidyut_artha": crosscheck[code]["artha"],
                "primary_iast": primary_iast,
                "vidyut_iast": vidyut_iast,
                "note": (
                    f"The primary record reads {primary_iast}; Vidyut reads "
                    f"{vidyut_iast}. The primary meaning is retained and the "
                    "Vidyut crosscheck is flagged_uncertain."
                ),
            }

    roots.sort(key=lambda item: _code_key(item["baseindex"]))
    tier_counts = Counter(item["tier"] for item in roots)
    gana_counts = Counter(int(row["gana"]) for row in selected)
    common_count = sum(
        1 for row in selected if "common" in row.get("tags", "").split(",")
    )

    return {
        "target_count": len(roots),
        "universe": (
            "All root records in the ashtadhyayi.com Dhātupāṭha dataset; "
            "gaṇasūtra rows and roots without an English gloss are excluded."
        ),
        "primary_source_id": PRIMARY_SOURCE_ID,
        "crosscheck_source_id": CROSSCHECK_SOURCE_ID,
        "source_row_count": len(source_rows),
        "root_record_count": len(root_rows),
        "common_count": common_count,
        "selection_note": (
            f"Complete Dhātupāṭha root corpus: {len(roots)} roots from "
            f"{len(root_rows)} root records. The {len(ganasutra_rows)} "
            "gaṇasūtra rows are sūtra records, not roots. Roots without an "
            "English gloss are excluded ("
            + ", ".join(row["baseindex"] for row in missing_english)
            + "). The original 210 common roots retain their core/additional/"
            "extended tiers; all other roots use the outside_common tier."
        ),
        "exclusions": {
            "ganasutra": {
                "count": len(ganasutra_rows),
                "codes": sorted(
                    (row["baseindex"] for row in ganasutra_rows), key=_code_key
                ),
                "reason": "Gaṇasūtra records are sūtras within the Dhātupāṭha, not dhātus.",
            },
            "missing_english": [
                {
                    "baseindex": row["baseindex"],
                    "reason": "No artha_english value is supplied by the primary dataset.",
                }
                for row in sorted(missing_english, key=lambda row: _code_key(row["baseindex"]))
            ],
        },
        "crosscheck_variants": variants,
        "tier_counts": {
            tier: tier_counts.get(tier, 0) for tier in TIER_ORDER
        },
        "gana_counts": {
            str(gana): count for gana, count in sorted(gana_counts.items())
        },
        "roots": roots,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the file is stale")
    args = parser.parse_args()

    payload = generate()
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    current = SELECTION_PATH.read_text(encoding="utf-8")
    if args.check:
        if rendered != current:
            raise SystemExit(
                "data/dhatu_selection.json is stale; run tools/generate_dhatus.py"
            )
        print("data/dhatu_selection.json is current")
        return
    SELECTION_PATH.write_text(rendered, encoding="utf-8")
    print(
        f"wrote {payload['target_count']} roots "
        f"({payload['source_row_count']} source rows, "
        f"{payload['tier_counts']['outside_common']} outside_common)"
    )


if __name__ == "__main__":
    main()

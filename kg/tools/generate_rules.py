#!/usr/bin/env python3
"""Regenerate data/rules.json from the pinned Vidyut sūtrapāṭha.

The selection is the complete sūtrapāṭha (adhyāyas 1-8). Existing curated
topics and relevant-term links are preserved. Use --check to verify that the
committed file is current.
"""

from __future__ import annotations

import argparse
import csv
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "data" / "rules.json"
TERMS_PATH = ROOT / "data" / "terms_vyakarana.json"
TSV_PATH = ROOT / "sources" / "cache" / "sutrapatha-vidyut.tsv"
SOURCE_ID = "src-vidyut-sutrapatha"


def _number_key(number: str) -> tuple[int, ...]:
    return tuple(int(part) for part in number.split("."))


def _load_rows() -> list[dict[str, str]]:
    with TSV_PATH.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _term_links() -> dict[str, list[str]]:
    if not TERMS_PATH.exists():
        return {}
    terms = json.loads(TERMS_PATH.read_text(encoding="utf-8"))["terms"]
    links: dict[str, list[str]] = {}
    for term in terms:
        target = term["claim"]["target"]
        links.setdefault(target, []).append(term["id"])
    return links


def generate() -> dict[str, Any]:
    existing_payload = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    existing = {rule["number"]: rule for rule in existing_payload["rules"]}
    rows = _load_rows()
    source_rows = {row["code"]: row["text"] for row in rows}
    if len(source_rows) != len(rows):
        raise SystemExit("duplicate rule numbers in Vidyut TSV")

    missing = set(existing) - set(source_rows)
    if missing:
        raise SystemExit(f"curated rule missing from Vidyut TSV: {sorted(missing)[0]}")

    merged: dict[str, dict[str, Any]] = {}
    for number, text in source_rows.items():
        rule = deepcopy(existing.get(number, {}))
        rule.setdefault("id", f"rule-{number.replace('.', '-')}")
        if rule.get("slp1", text) != text:
            raise SystemExit(f"curated rule text differs from Vidyut TSV: {number}")
        rule["number"] = number
        rule["slp1"] = text
        merged[number] = rule

    links = _term_links()
    rule_ids = {rule["id"]: number for number, rule in merged.items()}
    for rule_id, term_ids in links.items():
        number = rule_ids.get(rule_id)
        if number is None:
            continue
        relevant = merged[number].setdefault("relevant_terms", [])
        for term_id in term_ids:
            if term_id not in relevant:
                relevant.append(term_id)

    rules = [merged[number] for number in sorted(merged, key=_number_key)]
    return {
        "selection": {
            "source_id": SOURCE_ID,
            "scope": "All sūtras of the Vidyut Aṣṭādhyāyī sūtrapāṭha (adhyāyas 1-8).",
            "source_sutra_count": len(source_rows),
            "curated_topic_count": sum(1 for rule in rules if rule.get("topic")),
            "total": len(rules),
            "crosscheck_note": (
                "Vidyut is the sole build source. A separate comparison against the "
                "read-only iks-core Pāṇini fixture is documented in README and is not "
                "a build dependency."
            ),
        },
        "rules": rules,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the file is stale")
    args = parser.parse_args()

    payload = generate()
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    current = RULES_PATH.read_text(encoding="utf-8")
    if args.check:
        if rendered != current:
            raise SystemExit("data/rules.json is stale; run tools/generate_rules.py")
        print("data/rules.json is current")
        return
    RULES_PATH.write_text(rendered, encoding="utf-8")
    counts = payload["selection"]
    print(
        f"wrote {counts['total']} rules "
        f"({counts['curated_topic_count']} curated topics, "
        f"{counts['source_sutra_count']} source rows)"
    )


if __name__ == "__main__":
    main()

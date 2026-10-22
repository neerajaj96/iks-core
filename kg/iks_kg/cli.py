"""Command-line interface for the IKS knowledge graph."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rdflib import Graph

from .build import DIST_DIR, REPORT_DIR, build, validate, write_outputs
from .errors import BuildError


def _print_json(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def cmd_build(_: argparse.Namespace) -> int:
    graph, stats, coverage, audit = build()
    conforms, results_text = validate(graph)
    validation = {
        "conforms": conforms,
        "results_text": results_text,
        "evidence_audit": audit,
    }
    write_outputs(graph, stats, coverage, audit, validation)
    _print_json({"stats": stats, "validation": {"conforms": conforms}})
    return 0 if conforms else 1


def cmd_validate(_: argparse.Namespace) -> int:
    graph = Graph()
    graph.parse(DIST_DIR / "iks-kg.ttl", format="turtle")
    conforms, results_text = validate(graph)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "validation.json").write_text(
        json.dumps({"conforms": conforms, "results_text": results_text}, indent=2) + "\n",
        encoding="utf-8",
    )
    _print_json({"conforms": conforms})
    if not conforms:
        print(results_text, file=sys.stderr)
    return 0 if conforms else 1


def cmd_stats(_: argparse.Namespace) -> int:
    _, stats, coverage, _ = build()
    _print_json({"stats": stats, "coverage": coverage})
    return 0


def cmd_check_evidence(_: argparse.Namespace) -> int:
    _, _, _, audit = build()
    _print_json(audit)
    return 0 if not audit["problems"] and not audit["bad_status_claims"] else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="iks-kg")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("build", help="build dist/ and reports/")
    sub.add_parser("validate", help="validate dist/iks-kg.ttl against SHACL shapes")
    sub.add_parser("stats", help="print graph statistics")
    sub.add_parser("check-evidence", help="audit claim citations")
    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            return cmd_build(args)
        if args.command == "validate":
            return cmd_validate(args)
        if args.command == "stats":
            return cmd_stats(args)
        if args.command == "check-evidence":
            return cmd_check_evidence(args)
    except BuildError as exc:
        print(f"build error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

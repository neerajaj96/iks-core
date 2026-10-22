#!/usr/bin/env python3
"""Build deterministic explorer data from the published knowledge graph."""

from __future__ import annotations

import argparse
import gzip
import json
from collections import Counter
from pathlib import Path
from typing import Any

from rdflib import Graph, Namespace, RDF, URIRef

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs" / "kg"
DATA = DOCS / "data"
TTL_PATH = DOCS / "iks-kg.ttl.gz"
MANIFEST_PATH = DOCS / "manifest.json"
SELECTION_PATH = ROOT / "kg" / "data" / "dhatu_selection.json"
IKS = Namespace("urn:iks:")

OUTPUT_FILES = (
    "meta.json",
    "dhatus.json",
    "rules.json",
    "terms.json",
    "dhatu-claims.json",
    "rule-claims.json",
    "term-claims.json",
)


def fail(message: str) -> None:
    raise SystemExit(f"explorer build failed: {message}")


def local_name(value: Any) -> str:
    return str(value).rsplit(":", 1)[-1] if value is not None else ""


def text(graph: Graph, subject: URIRef, predicate: URIRef) -> str:
    value = graph.value(subject, predicate)
    return str(value) if value is not None else ""


def number(graph: Graph, subject: URIRef, predicate: URIRef) -> int | None:
    value = graph.value(subject, predicate)
    return int(value) if value is not None else None


def claim_records(graph: Graph, node: URIRef) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for claim in sorted(graph.objects(node, IKS.hasClaim), key=str):
        citation = graph.value(claim, IKS.citation)
        if citation is None:
            fail(f"claim without citation: {claim}")
        records.append(
            {
                "id": local_name(claim),
                "relation": local_name(graph.value(claim, IKS.relation)),
                "status": text(graph, claim, IKS.verificationStatus),
                "method": text(graph, claim, IKS.method),
                "assertion": text(graph, claim, IKS.assertionType),
                "text": text(graph, claim, IKS.claimText),
                "known_issue": text(graph, claim, IKS.knownIssue),
                "citation": {
                    "source": local_name(graph.value(citation, IKS.source)),
                    "locator": text(graph, citation, IKS.locator),
                    "quote": text(graph, citation, IKS.evidenceQuote),
                    "span_start": number(graph, citation, IKS.spanStart),
                    "span_end": number(graph, citation, IKS.spanEnd),
                    "record_hash": text(graph, citation, IKS.recordHash),
                },
            }
        )
    return records


def primary_status(claims: list[dict[str, Any]]) -> str:
    for claim in claims:
        if claim["assertion"] == "lexical_attestation":
            return claim["status"]
    return claims[0]["status"] if claims else "unknown"


def generate() -> dict[str, Any]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    selection = json.loads(SELECTION_PATH.read_text(encoding="utf-8"))
    tiers = {row["baseindex"]: row["tier"] for row in selection["roots"]}

    graph = Graph()
    with gzip.open(TTL_PATH, "rt", encoding="utf-8") as handle:
        graph.parse(data=handle.read(), format="turtle")

    dhatus: list[dict[str, Any]] = []
    dhatu_claims: dict[str, list[dict[str, Any]]] = {}
    for node in graph.subjects(RDF.type, IKS.Dhatu):
        node_id = local_name(node)
        code = text(graph, node, IKS.dhatupathaCode)
        claims = claim_records(graph, node)
        dhatu_claims[node_id] = claims
        dhatus.append(
            {
                "id": node_id,
                "code": code,
                "root_iast": text(graph, node, IKS.rootIast),
                "root_sa": text(graph, node, IKS.rootSa),
                "root_slp1": text(graph, node, IKS.rootSlp1),
                "gana": number(graph, node, IKS.gana),
                "pada": text(graph, node, IKS.pada),
                "meaning_iast": text(graph, node, IKS.meaningIast),
                "meaning_sa": text(graph, node, IKS.meaningSa),
                "meaning_en": text(graph, node, IKS.meaningEn),
                "tier": tiers.get(code, ""),
                "status": primary_status(claims),
                "flagged": any(c["status"] == "flagged_uncertain" for c in claims),
            }
        )
    dhatus.sort(key=lambda row: tuple(int(part) for part in row["code"].split(".")))

    term_rows: list[dict[str, Any]] = []
    terms_by_rule: dict[str, list[dict[str, str]]] = {}
    term_claims: dict[str, list[dict[str, Any]]] = {}
    for node in graph.subjects(RDF.type, IKS.VyakaranaTerm):
        node_id = local_name(node)
        rule = graph.value(node, IKS.definedBy)
        rule_id = local_name(rule)
        rule_number = text(graph, rule, IKS.ruleNumber) if rule is not None else ""
        claims = claim_records(graph, node)
        term_claims[node_id] = claims
        row = {
            "id": node_id,
            "iast": text(graph, node, IKS.termIast),
            "sa": text(graph, node, IKS.termSa),
            "en": text(graph, node, IKS.termEn),
            "definition": text(graph, node, IKS.definition),
            "gloss_status": text(graph, node, IKS.glossStatus),
            "rule": rule_number,
            "rule_id": rule_id,
            "status": claims[0]["status"] if claims else "unknown",
        }
        term_rows.append(row)
        terms_by_rule.setdefault(rule_id, []).append(
            {"id": node_id, "iast": row["iast"], "en": row["en"]}
        )
    term_rows.sort(key=lambda row: row["iast"])

    rules: list[dict[str, Any]] = []
    rule_claims: dict[str, list[dict[str, Any]]] = {}
    for node in graph.subjects(RDF.type, IKS.Rule):
        node_id = local_name(node)
        claims = claim_records(graph, node)
        rule_claims[node_id] = claims
        rules.append(
            {
                "id": node_id,
                "number": text(graph, node, IKS.ruleNumber),
                "slp1": text(graph, node, IKS.ruleTextSlp1),
                "iast": text(graph, node, IKS.ruleTextIast),
                "sa": text(graph, node, IKS.ruleTextSa),
                "note": text(graph, node, IKS.note),
                "terms": terms_by_rule.get(node_id, []),
                "status": claims[0]["status"] if claims else "unknown",
            }
        )
    rules.sort(key=lambda row: tuple(int(part) for part in row["number"].split(".")))

    if len(dhatus) != manifest["stats"]["dhatus"]:
        fail(f"dhātu count mismatch: {len(dhatus)}")
    if len(rules) != manifest["stats"]["rules"]:
        fail(f"rule count mismatch: {len(rules)}")
    if len(term_rows) != manifest["stats"]["terms"]:
        fail(f"term count mismatch: {len(term_rows)}")

    status_counts = Counter(
        claim["status"]
        for claims in (dhatu_claims, rule_claims, term_claims)
        for group in claims.values()
        for claim in group
    )

    meta = {
        "name": manifest["name"],
        "version": manifest["version"],
        "published_at": manifest["published_at"],
        "release": manifest["release"],
        "counts": {
            "triples": manifest["stats"]["triples"],
            "claims": manifest["stats"]["claims"],
            "citations": manifest["stats"]["citations"],
            "dhatus": len(dhatus),
            "rules": len(rules),
            "terms": len(term_rows),
            "knowledge_entities": manifest["stats"]["knowledge_entities"],
            "explorer_claims": sum(status_counts.values()),
        },
        "graph_status_counts": manifest["verification"]["status_counts"],
        "explorer_status_counts": dict(sorted(status_counts.items())),
        "tiers": dict(sorted(Counter(row["tier"] for row in dhatus).items())),
        "ganas": {
            str(gana): count
            for gana, count in sorted(
                Counter(row["gana"] for row in dhatus if row["gana"] is not None).items()
            )
        },
        "padas": dict(sorted(Counter(row["pada"] for row in dhatus).items())),
        "topics": sorted({row["note"] for row in rules if row["note"]}),
    }

    if sum(status_counts.values()) != meta["counts"]["explorer_claims"]:
        fail("claim count mismatch")
    return {
        "meta.json": meta,
        "dhatus.json": dhatus,
        "rules.json": rules,
        "terms.json": term_rows,
        "dhatu-claims.json": dhatu_claims,
        "rule-claims.json": rule_claims,
        "term-claims.json": term_claims,
    }


def render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if committed data is stale")
    args = parser.parse_args()

    outputs = generate()
    DATA.mkdir(parents=True, exist_ok=True)
    stale: list[str] = []
    for name in OUTPUT_FILES:
        path = DATA / name
        rendered = render(outputs[name])
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        if args.check:
            if current != rendered:
                stale.append(name)
        else:
            path.write_text(rendered, encoding="utf-8")

    if args.check:
        if stale:
            fail(f"stale explorer data: {', '.join(stale)}; run tools/build_explorer.py")
        print("explorer data is current")
        return

    total = sum((DATA / name).stat().st_size for name in OUTPUT_FILES)
    print(
        f"wrote {len(OUTPUT_FILES)} explorer files "
        f"({outputs['meta.json']['counts']['dhatus']} dhātus, "
        f"{outputs['meta.json']['counts']['rules']} rules, "
        f"{outputs['meta.json']['counts']['terms']} terms, {total} bytes)"
    )


if __name__ == "__main__":
    main()

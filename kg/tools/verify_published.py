#!/usr/bin/env python3
"""Verify the published IKS Knowledge Graph artifacts in docs/kg."""

from __future__ import annotations

import gzip
import hashlib
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from pyshacl import validate
from rdflib import Graph, Namespace, RDF

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs" / "kg"
IKS = Namespace("urn:iks:")

EXPECTED_VERSION = "0.1.0"
EXPECTED_TAG = "kg-v0.1.0"
EXPECTED_STATS = {
    "triples": 246010,
    "claims": 8618,
    "citations": 8618,
    "dhatus": 2228,
    "rules": 3983,
    "terms": 37,
    "knowledge_entities": 6373,
    "span_citations": 4153,
    "record_hash_citations": 4465,
}
EXPECTED_STATUS = {
    "verified_primary": 6351,
    "verified_secondary": 2258,
    "flagged_uncertain": 9,
}
REQUIRED_ARTIFACTS = {
    "iks-kg.ttl.gz",
    "iks-kg.nt.gz",
    "iks-kg.jsonld.gz",
    "iks-kg.shacl.ttl",
    "iks-kg.context.jsonld",
    "coverage.json",
    "summary.md",
    "README.md",
    "SHA256SUMS",
}


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        for name in ("href", "src"):
            link = values.get(name)
            if link:
                self.links.append(link)


def fail(message: str) -> None:
    raise SystemExit(f"published artifact verification failed: {message}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_artifacts(manifest: dict[str, Any]) -> None:
    artifacts = {item["name"]: item for item in manifest["artifacts"]}
    if set(artifacts) != REQUIRED_ARTIFACTS:
        missing = REQUIRED_ARTIFACTS - set(artifacts)
        extra = set(artifacts) - REQUIRED_ARTIFACTS
        fail(f"artifact manifest mismatch; missing={sorted(missing)} extra={sorted(extra)}")

    sums: dict[str, str] = {}
    for line in (DOCS / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        digest, name = line.split(maxsplit=1)
        name = name.strip().lstrip("*")
        if name in sums:
            fail(f"duplicate checksum entry: {name}")
        sums[name] = digest

    for name, item in artifacts.items():
        path = DOCS / name
        if not path.is_file():
            fail(f"missing artifact: {name}")
        if path.stat().st_size != item["bytes"]:
            fail(f"size mismatch for {name}")
        if sha256(path) != item["sha256"]:
            fail(f"manifest hash mismatch for {name}")
        if name != "SHA256SUMS":
            if name not in sums:
                fail(f"missing SHA256SUMS entry for {name}")
            if sums[name] != item["sha256"]:
                fail(f"SHA256SUMS mismatch for {name}")

    expected_sums = set(artifacts) - {"SHA256SUMS"}
    if set(sums) != expected_sums:
        fail(f"SHA256SUMS entries mismatch; expected={sorted(expected_sums)}")


def parse_graph(name: str, fmt: str) -> Graph:
    with gzip.open(DOCS / name, "rt", encoding="utf-8") as handle:
        data = handle.read()
    graph = Graph()
    graph.parse(data=data, format=fmt)
    return graph


def verify_graph(graph: Graph) -> None:
    citations = set(graph.subjects(RDF.type, IKS.Citation))
    actual = {
        "triples": len(graph),
        "claims": len(set(graph.subjects(RDF.type, IKS.Claim))),
        "citations": len(citations),
        "dhatus": len(set(graph.subjects(RDF.type, IKS.Dhatu))),
        "rules": len(set(graph.subjects(RDF.type, IKS.Rule))),
        "terms": len(set(graph.subjects(RDF.type, IKS.VyakaranaTerm))),
        "knowledge_entities": len(
            set(graph.subjects(RDF.type, IKS.KnowledgeEntity))
        ),
        "span_citations": sum(1 for c in citations if any(graph.objects(c, IKS.spanStart))),
        "record_hash_citations": sum(
            1 for c in citations if any(graph.objects(c, IKS.recordHash))
        ),
    }
    for key, expected in EXPECTED_STATS.items():
        if actual[key] != expected:
            fail(f"{key} count mismatch: {actual[key]} != {expected}")


def verify_status(manifest: dict[str, Any]) -> None:
    status = manifest["verification"]["status_counts"]
    if status != EXPECTED_STATUS:
        fail(f"status counts mismatch: {status} != {EXPECTED_STATUS}")
    if manifest["verification"]["shacl_conforms"] is not True:
        fail("manifest does not report SHACL conformance")
    if manifest["verification"]["evidence_audit_problems"] != 0:
        fail("manifest reports evidence audit problems")


def verify_coverage() -> None:
    coverage = load_json(DOCS / "coverage.json")
    expected = {
        "dhatus": EXPECTED_STATS["dhatus"],
        "rules": EXPECTED_STATS["rules"],
        "terms": EXPECTED_STATS["terms"],
        "claims": EXPECTED_STATS["claims"],
        "citation_count": EXPECTED_STATS["citations"],
        "knowledge_entities": EXPECTED_STATS["knowledge_entities"],
    }
    for key, value in expected.items():
        if coverage.get(key) != value:
            fail(f"coverage mismatch for {key}: {coverage.get(key)} != {value}")


def verify_manifest(manifest: dict[str, Any]) -> None:
    if manifest.get("version") != EXPECTED_VERSION:
        fail(f"unexpected version: {manifest.get('version')}")
    release = manifest.get("release", {})
    if release.get("tag") != EXPECTED_TAG:
        fail(f"unexpected release tag: {release.get('tag')}")
    if manifest.get("stats") != EXPECTED_STATS:
        fail("manifest stats do not match the expected published counts")
    verify_status(manifest)


def verify_shacl(graph: Graph) -> None:
    shapes = Graph().parse(DOCS / "iks-kg.shacl.ttl", format="turtle")
    conforms, _, results = validate(
        graph,
        shacl_graph=shapes,
        inference=None,
        abort_on_first=False,
        allow_infos=False,
        allow_warnings=False,
    )
    if not conforms:
        fail(f"SHACL validation failed:\n{results}")


def verify_links() -> None:
    pages = [ROOT / "docs" / "index.html", DOCS / "index.html"]
    for page in pages:
        parser = LinkParser()
        parser.feed(page.read_text(encoding="utf-8"))
        for link in parser.links:
            if link.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target = (page.parent / link.split("#", 1)[0]).resolve()
            if not target.exists():
                fail(f"broken link in {page.relative_to(ROOT)}: {link}")
            if ROOT not in target.parents and target != ROOT:
                fail(f"link escapes repository in {page.relative_to(ROOT)}: {link}")


def main() -> None:
    manifest = load_json(DOCS / "manifest.json")
    verify_manifest(manifest)
    verify_artifacts(manifest)
    verify_coverage()

    ttl = parse_graph("iks-kg.ttl.gz", "turtle")
    verify_graph(ttl)
    for name, fmt in (
        ("iks-kg.nt.gz", "nt"),
        ("iks-kg.jsonld.gz", "json-ld"),
    ):
        graph = parse_graph(name, fmt)
        if len(graph) != EXPECTED_STATS["triples"]:
            fail(f"{name} triple count mismatch: {len(graph)}")
    verify_shacl(ttl)
    verify_links()

    print(
        "verified "
        f"{len(REQUIRED_ARTIFACTS)} artifacts, "
        f"{EXPECTED_STATS['triples']} triples, "
        f"{EXPECTED_STATS['claims']} claims, "
        f"SHACL conforms, links ok"
    )


if __name__ == "__main__":
    main()

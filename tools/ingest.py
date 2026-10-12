"""Ingest pipeline: SARIT/GRETIL/Wikisource fetchers with offline-seed fallback.

Gold-standard rule: every record emitted carries explicit provenance
{tier: verbatim | famous-gist | topic-digest, note, verify}.
Network is best-effort; CI never fails on fetch (falls back to curated seeds).
"""
from __future__ import annotations
import json
import urllib.request
from pathlib import Path

SOURCES = {
    "sarit": "https://sarit.indology.info",
    "gretil": "https://gretil.sub.uni-goettingen.de",
    "wikisource": "https://sa.wikisource.org",
    "archive": "https://archive.org",
}

TIERS = ("verbatim", "famous-gist", "topic-digest")


def try_fetch(url: str, timeout: int = 15) -> str | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "iks-core-ingest/2.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read(200_000).decode("utf-8", "replace")
    except Exception:
        return None


def provenance(tier: str, note: str, verify: str = "SARIT/GRETIL edition") -> dict:
    assert tier in TIERS, tier
    return {"tier": tier, "note": note, "verifyAgainst": verify}


def normalize_iast(s: str) -> str:
    return s.strip().replace("  ", " ")


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def mirror_to_docs(repo_root: Path, name: str, obj) -> None:
    write_json(repo_root / "docs" / "data" / name, obj)

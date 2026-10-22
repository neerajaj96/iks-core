"""Source manifest loading and witness-text normalization."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from functools import lru_cache
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from .errors import BuildError
from .translit import normalize_for_source

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
SOURCE_DIR = ROOT / "sources" / "cache"


@dataclass(frozen=True)
class Source:
    id: str
    source_type: str
    title: str
    url: str
    local_path: str
    retrieved_at: str
    sha256: str
    license: str
    extraction: str
    language: str
    script: str
    quality: str
    notes: str
    author: str = ""
    edition: str = ""
    publisher: str = ""
    bytes: int = 0

    @property
    def path(self) -> Path:
        return ROOT / self.local_path

    @property
    def script_name(self) -> str:
        return self.script


class _VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self._skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self._skip:
            self._skip -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip:
            self._parts.append(data)

    def text(self) -> str:
        return " ".join(self._parts)


def _strip_html(raw: str) -> str:
    parser = _VisibleText()
    parser.feed(raw)
    parser.close()
    return parser.text()


_TEXTGRID_BRACKETS = re.compile(r"\[[^\]]*\]")
_TEXTGRID_PARENS = re.compile(r"\([^)]*\)")


def _strip_textgrid_markup(raw: str) -> str:
    raw = _TEXTGRID_BRACKETS.sub(" ", raw)
    raw = _TEXTGRID_PARENS.sub(" ", raw)
    return raw.replace("*", "")


def load_sources() -> dict[str, Source]:
    payload = json.loads((DATA_DIR / "sources.json").read_text(encoding="utf-8"))
    sources: dict[str, Source] = {}
    for item in payload["sources"]:
        source = Source(**{k: item.get(k, "") for k in Source.__dataclass_fields__})
        if source.path.suffix == ".json" and source.bytes:
            pass
        if not source.path.exists():
            raise BuildError(f"missing source snapshot: {source.local_path}")
        actual = hashlib.sha256(source.path.read_bytes()).hexdigest()
        if actual != source.sha256:
            raise BuildError(
                f"source hash mismatch for {source.id}: manifest={source.sha256} actual={actual}"
            )
        sources[source.id] = source
    return sources


@lru_cache(maxsize=None)
def raw_text(source_id: str) -> str:
    source = load_sources()[source_id]
    return source.path.read_text(encoding="utf-8", errors="replace")


@lru_cache(maxsize=None)
def witness_text(source_id: str) -> str:
    """Return a normalized IAST text used only for evidence matching."""

    source = load_sources()[source_id]
    raw = raw_text(source_id)
    if source.extraction == "html":
        raw = _strip_html(raw)
    elif source.extraction == "textgrid":
        raw = _strip_textgrid_markup(raw)
    elif source.extraction == "itrans":
        from .translit import to_iast

        raw = to_iast(raw, "ITRANS")
    elif source.extraction == "tsv":
        from .translit import to_iast

        raw = to_iast(raw, "SLP1")
    elif source.script not in {"IAST", ""}:
        from .translit import to_iast

        raw = to_iast(raw, source.script)  # type: ignore[arg-type]
    return normalize_for_source(raw, "IAST")


@lru_cache(maxsize=None)
def tsv_row_spans(source_id: str) -> dict[str, tuple[int, int, str]]:
    """Return exact normalized-text offsets for each TSV row."""

    source = load_sources()[source_id]
    if source.extraction != "tsv":
        raise BuildError(f"source is not a TSV dataset: {source_id}")
    raw = raw_text(source_id)
    lines = raw.splitlines()
    if not lines:
        raise BuildError(f"empty TSV source: {source_id}")
    text = witness_text(source_id)
    offset = len(normalize_for_source(lines[0], source.script))  # type: ignore[arg-type]
    spans: dict[str, tuple[int, int, str]] = {}
    for line in lines[1:]:
        if not line.strip():
            continue
        code, separator, row_text = line.partition("\t")
        if not separator:
            raise BuildError(f"malformed TSV row in {source_id}: {line!r}")
        if code in spans:
            raise BuildError(f"duplicate TSV row code in {source_id}: {code}")
        normalized = normalize_for_source(row_text, source.script)  # type: ignore[arg-type]
        end = offset + len(normalized)
        quote = text[offset:end]
        if quote != normalized:
            raise BuildError(
                f"TSV row alignment mismatch in {source_id}: {code!r}"
            )
        spans[code] = (offset, end, quote)
        offset = end
    if offset != len(text):
        raise BuildError(
            f"TSV span coverage mismatch in {source_id}: {offset} != {len(text)}"
        )
    return spans


def find_tsv_row_span(source_id: str, row_code: str) -> tuple[int, int, str]:
    """Find the exact normalized span of one TSV row by its code."""

    spans = tsv_row_spans(source_id)
    try:
        return spans[row_code]
    except KeyError as exc:
        raise BuildError(
            f"TSV row code not found in {source_id}: {row_code!r}"
        ) from exc


def find_span(
    source_id: str,
    anchor: str,
    anchor_script: str = "IAST",
    anchor_after: str | None = None,
    anchor_after_script: str = "IAST",
) -> tuple[int, int, str]:
    """Find an anchor in normalized witness text.

    When `anchor_after` is given, the search starts at that normalized context
    anchor (inclusive), which prevents accidental matches on an earlier
    occurrence elsewhere in the source.

    Returns (start, end, normalized_quote). The offsets refer to the normalized
    witness text, not the raw file; citations record that basis explicitly.
    """

    source = load_sources()[source_id]
    if anchor_script not in {"IAST", "SLP1", "ITRANS", "Devanagari"}:
        raise BuildError(f"unsupported anchor script: {anchor_script}")
    if anchor_after_script not in {"IAST", "SLP1", "ITRANS", "Devanagari"}:
        raise BuildError(f"unsupported anchor-after script: {anchor_after_script}")
    anchor_normalized = normalize_for_source(anchor, anchor_script)  # type: ignore[arg-type]
    text = witness_text(source_id)
    search_start = 0
    if anchor_after is not None:
        context_normalized = normalize_for_source(anchor_after, anchor_after_script)  # type: ignore[arg-type]
        search_start = text.find(context_normalized)
        if search_start < 0:
            raise BuildError(
                f"anchor-after context not found in {source_id}: {anchor_after!r} "
                f"(normalized={context_normalized!r})"
            )
    start = text.find(anchor_normalized, search_start)
    if start < 0:
        raise BuildError(
            f"evidence anchor not found in {source_id}: {anchor!r} "
            f"(normalized={anchor_normalized!r})"
        )
    end = start + len(anchor_normalized)
    return start, end, text[start:end]


def canonical_hash(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

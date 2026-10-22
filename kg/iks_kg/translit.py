"""Transliteration and evidence-normalization helpers."""

from __future__ import annotations

import re
import unicodedata
from typing import Literal

from indic_transliteration import sanscript

Script = Literal["IAST", "SLP1", "ITRANS", "Devanagari"]

_SCRIPT_MAP = {
    "IAST": sanscript.IAST,
    "SLP1": sanscript.SLP1,
    "ITRANS": sanscript.ITRANS,
    "Devanagari": sanscript.DEVANAGARI,
}


def transliterate(text: str, source: Script, target: Script) -> str:
    if source == target:
        return text
    return sanscript.transliterate(text, _SCRIPT_MAP[source], _SCRIPT_MAP[target])


def to_iast(text: str, script: Script) -> str:
    return transliterate(text, script, "IAST")


def to_slp1(text: str, script: Script) -> str:
    return transliterate(text, script, "SLP1")


def to_devanagari(text: str, script: Script) -> str:
    return transliterate(text, script, "Devanagari")


def normalize_iast(text: str) -> str:
    """Normalize Sanskrit text for exact-ish evidence matching.

    The normalized form is NFC, case-folded IAST with punctuation, spaces, and
    digits removed. This makes witness variants such as hyphenation and line
    breaks comparable without changing the underlying source span.
    """

    text = unicodedata.normalize("NFC", text)
    text = text.casefold()
    kept: list[str] = []
    for char in text:
        if char.isalpha() or unicodedata.combining(char):
            kept.append(char)
    return "".join(kept)


def normalize_for_source(text: str, script: Script) -> str:
    return normalize_iast(to_iast(text, script) if script != "IAST" else text)


def slug(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "item"

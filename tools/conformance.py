"""Conformance: every data record validates (required fields + cross-refs + content-hash uniqueness). Stdlib only."""
from __future__ import annotations
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "texts.json": ["id", "titleSanskrit", "titleEnglish", "authorIds", "layer", "darsana"],
    "sutras.json": ["id", "textId", "adhyaNotation", "sanskrit", "translation", "confidence"],
    "terms.json": ["id", "sanskrit", "iast", "darsanaScope", "definitionSutras", "ontologicalSort", "formalSymbol"],
    "inferences.json": ["id", "school", "form", "paksa", "sadhya", "hetu", "vyapti", "hetvabhasa",
                        "trairupya", "drstanta"],
    "vada_nodes.json": ["id", "textId", "sutraRefs", "siddhanta", "katha"],
    "vada_edges.json": ["id", "from", "to", "kind", "fallacyCharged", "refutationTextId", "locus", "weight"],
    "cognitions.json": ["id", "content", "pramana", "state", "valid", "standpointQualifier"],
}


def main() -> int:
    errors: list[str] = []
    store = {}
    for name, req in REQUIRED.items():
        p = ROOT / "data" / name
        if not p.exists():
            errors.append(f"missing {name}")
            continue
        recs = json.loads(p.read_text(encoding="utf-8"))
        store[name] = recs
        ids = set()
        for r in recs:
            for f in req:
                if f not in r:
                    errors.append(f"{name}:{r.get('id', '?')} missing field {f}")
            if r.get("id") in ids:
                errors.append(f"{name}: duplicate id {r.get('id')}")
            ids.add(r.get("id"))
    texts = {t["id"] for t in store.get("texts.json", [])}
    sutras = {s["id"] for s in store.get("sutras.json", [])}
    for s in store.get("sutras.json", []):
        if s["textId"] not in texts:
            errors.append(f"sutras.json:{s['id']} unknown textId {s['textId']}")
        if s.get("confidence") not in ("verbatim", "famous-gist", "topic-digest"):
            errors.append(f"sutras.json:{s['id']} bad confidence tier")
    for t in store.get("terms.json", []):
        for ds in t.get("definitionSutras", []):
            if ds not in sutras:
                errors.append(f"terms.json:{t['id']} unknown sutra {ds}")
    nodes = {n["id"] for n in store.get("vada_nodes.json", [])}
    for n in store.get("vada_nodes.json", []):
        if n["textId"] not in texts:
            errors.append(f"vada_nodes.json:{n['id']} unknown textId {n['textId']}")
        for sr in n.get("sutraRefs", []):
            if sr not in sutras:
                errors.append(f"vada_nodes.json:{n['id']} unknown sutra {sr}")
    for e in store.get("vada_edges.json", []):
        if e["from"] not in nodes or e["to"] not in nodes:
            errors.append(f"vada_edges.json:{e['id']} dangling endpoint")
        if not (0.0 <= float(e["weight"]) <= 1.0):
            errors.append(f"vada_edges.json:{e['id']} weight out of range")
    # content-hash uniqueness: same normalized wording twice in one text = duplicate,
    # unless explicitly linked as edition repetition via sameWordingAs
    seen: dict[tuple, str] = {}
    byid = {s["id"]: s for s in store.get("sutras.json", [])}
    for s in store.get("sutras.json", []):
        norm = re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", s.get("sanskrit", ""))
                      .encode("ascii", "ignore").decode().lower())
        key = (s.get("textId"), norm)
        if key in seen:
            other = seen[key]
            linked = (s.get("sameWordingAs") == other
                      or byid.get(other, {}).get("sameWordingAs") == s["id"])
            if not linked:
                errors.append(f"sutras.json:{s['id']} duplicates content of {other}")
        else:
            seen[key] = s["id"]
    counts = {k: len(v) for k, v in store.items()}
    print("counts:", counts)
    if errors:
        print(f"FAIL: {len(errors)} errors")
        for er in errors[:30]:
            print(" -", er)
        return 1
    print("conformance OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

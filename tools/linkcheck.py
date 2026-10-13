"""Link tools: audit candidate URLs (keep only live ones) + CI check of stored corpusRefs.

Usage:
  python3 tools/linkcheck.py --audit tools/link_candidates.json   # print live/dead per text
  python3 tools/linkcheck.py --check                               # verify data/texts.json refs (CI)
"""
from __future__ import annotations
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UA = {"User-Agent": "iks-core-linkcheck/2.7 (contact: repo issues)"}


def head_ok(url: str, timeout: int = 20) -> tuple[bool, str]:
    try:
        from urllib.parse import urlsplit, urlunsplit, quote
        parts = urlsplit(url)
        host = parts.hostname.encode("idna").decode("ascii") if parts.hostname else ""
        netloc = host + (f":{parts.port}" if parts.port else "")
        path = quote(parts.path, safe="/%")
        url = urlunsplit((parts.scheme, netloc, path, parts.query, parts.fragment))
    except Exception:
        pass
    try:
        req = urllib.request.Request(url, headers=UA, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return (200 <= r.status < 400, str(r.status))
    except Exception as e:
        try:  # some hosts reject HEAD; retry GET (first bytes)
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                r.read(1)
                return (200 <= r.status < 400, str(r.status))
        except Exception as e2:
            return (False, f"{type(e2).__name__}: {e2}"[:120])


def audit(cands: dict) -> None:
    for tid, urls in cands.items():
        for u in urls:
            ok, info = head_ok(u)
            print(("LIVE " if ok else "DEAD ") + f"{tid} {info} {u}")


def check() -> int:
    texts = json.loads((ROOT / "data" / "texts.json").read_text(encoding="utf-8"))
    bad = 0
    for t in texts:
        refs = t.get("corpusRefs", {}) or {}
        if t.get("noStableEtext"):
            if refs:
                print(f"WARN {t['id']}: noStableEtext but refs present")
            continue
        if not refs:
            print(f"FAIL {t['id']}: no refs and no noStableEtext flag")
            bad += 1
            continue
        for k, u in refs.items():
            ok, info = head_ok(u)
            print(("ok " if ok else "DEAD ") + f"{t['id']}.{k} {info}")
            if not ok:
                bad += 1
    print("linkcheck:", "OK" if bad == 0 else f"{bad} problems")
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--audit":
        audit(json.loads(Path(sys.argv[2]).read_text(encoding="utf-8")))
    elif len(sys.argv) == 2 and sys.argv[1] == "--check":
        sys.exit(check())
    else:
        print(__doc__)

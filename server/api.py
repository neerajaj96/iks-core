"""IKS-Core query API: corpus search, vada graph analytics, anumana validation.

FastAPI when installed (Swagger at /docs); stdlib http.server fallback otherwise.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.vada.graph import load_seed  # noqa: E402
from src.logic.iks_nn import hill_inference, floor_absence  # noqa: E402
from src.logic.anumana import detect_hetvabhasa  # noqa: E402
from src.ontology.pramana import PRAMANA_SETS  # noqa: E402

DATA = ROOT / "data"


def load(name: str):
    p = DATA / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def search_sutras(q: str = "", text: str = "", confidence: str = "") -> list:
    out = load("sutras.json")
    if text:
        out = [r for r in out if r.get("textId") == text]
    if confidence:
        out = [r for r in out if r.get("confidence") == confidence]
    if q:
        ql = q.lower()
        out = [r for r in out if ql in (r.get("sanskrit", "") + r.get("translation", "")).lower()]
    return out


def validate_anumana(body: dict) -> dict:
    code = detect_hetvabhasa(
        bool(body.get("paksadharmata", True)),
        bool(body.get("sapakse", True)),
        bool(body.get("vipakse_present", False)),
        bool(body.get("contradicts_sadhya", False)),
        bool(body.get("defeated", False)),
        bool(body.get("counter_reason", False)),
    )
    grounded = True
    if body.get("form") == "Nyaya-5" and not body.get("drstanta"):
        code, grounded = "Asiddha", False
    return {"valid": code == "none", "hetvabhasa": code, "grounded": grounded}


try:
    from fastapi import FastAPI, Query  # type: ignore
    from pydantic import BaseModel  # type: ignore
    HAS_FASTAPI = True
except Exception:
    HAS_FASTAPI = False

if HAS_FASTAPI:
    app = FastAPI(title="IKS-Core API", version="2.0.0",
                  description="IKS-MAM query layer: corpus, pramana, vada graph, anumana validation")

    class AnumanaBody(BaseModel):
        paksadharmata: bool = True
        sapakse: bool = True
        vipakse_present: bool = False
        contradicts_sadhya: bool = False
        defeated: bool = False
        counter_reason: bool = False
        form: str = "Nyaya-5"
        drstanta: str = ""

    @app.get("/health")
    def health():
        return {"ok": True, "version": "2.0.0"}

    @app.get("/pramana")
    def pramana():
        return {k: sorted(v) for k, v in PRAMANA_SETS.items()}

    @app.get("/texts")
    def texts():
        return load("texts.json")

    @app.get("/texts/{tid}")
    def text_one(tid: str):
        for t in load("texts.json"):
            if t["id"] == tid:
                return t
        return {"error": "not found"}

    @app.get("/sutras")
    def sutras(q: str = Query(""), text: str = Query(""), confidence: str = Query("")):
        return search_sutras(q, text, confidence)

    @app.get("/sutras/{sid}")
    def sutra_one(sid: str):
        for s in load("sutras.json"):
            if s["id"] == sid:
                return s
        return {"error": "not found"}

    @app.get("/terms")
    def terms():
        return load("terms.json")

    @app.get("/inferences")
    def inferences():
        return load("inferences.json")

    @app.get("/cognitions")
    def cognitions():
        return load("cognitions.json")

    @app.get("/vada")
    def vada():
        g = load_seed()
        return {"nodes": g.nodes, "edges": g.edges, "summary": g.summary()}

    @app.get("/graph")
    def graph(katha: str = Query("")):
        g = load_seed()
        if katha:
            g = g.filter_by_katha(katha)
        return {"summary": g.summary(), "rank": g.pagerank(),
                "fallacies": g.fallacy_histogram(), "degrees": g.weighted_degree()}

    @app.get("/graph/export")
    def graph_export():
        return load_seed().d3_export()

    @app.post("/anuman/validate")
    def anuman_validate(body: AnumanaBody):
        return validate_anumana(body.model_dump())

    @app.get("/demo/hill")
    def hill():
        return hill_inference()

    @app.get("/demo/absence")
    def absence():
        return {"render": floor_absence()}

    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
else:
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from urllib.parse import urlparse, parse_qs

    class H(BaseHTTPRequestHandler):
        def _send(self, obj, code=200):
            data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            u = urlparse(self.path)
            qs = parse_qs(u.query)
            g = load_seed()
            if u.path == "/texts":
                self._send(load("texts.json"))
            elif u.path == "/sutras":
                self._send(search_sutras(qs.get("q", [""])[0], qs.get("text", [""])[0],
                                         qs.get("confidence", [""])[0]))
            elif u.path == "/terms":
                self._send(load("terms.json"))
            elif u.path == "/inferences":
                self._send(load("inferences.json"))
            elif u.path == "/cognitions":
                self._send(load("cognitions.json"))
            elif u.path == "/vada":
                self._send({"nodes": g.nodes, "edges": g.edges, "summary": g.summary()})
            elif u.path == "/graph":
                k = qs.get("katha", [""])[0]
                if k:
                    g = g.filter_by_katha(k)
                self._send({"summary": g.summary(), "rank": g.pagerank(),
                            "fallacies": g.fallacy_histogram()})
            elif u.path == "/graph/export":
                self._send(g.d3_export())
            elif u.path == "/pramana":
                self._send({k: sorted(v) for k, v in PRAMANA_SETS.items()})
            else:
                self._send({"ok": True, "hill": hill_inference(),
                            "absence": floor_absence(),
                            "note": "stdlib fallback; install fastapi for full router + POST /anuman/validate"})

        def do_POST(self):
            u = urlparse(self.path)
            if u.path == "/anuman/validate":
                n = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(n) or b"{}")
                self._send(validate_anumana(body))
            else:
                self._send({"error": "not found"}, 404)

        def log_message(self, *a):
            pass

    if __name__ == "__main__":
        print("IKS-Core API (stdlib) on http://0.0.0.0:8000")
        HTTPServer(("0.0.0.0", 8000), H).serve_forever()

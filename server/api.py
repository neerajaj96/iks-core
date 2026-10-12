"""Demo read-only API. Uses FastAPI if installed, else stdlib http.server fallback."""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from fastapi import FastAPI
    import uvicorn
    HAS_FASTAPI = True
except Exception:
    HAS_FASTAPI = False

from src.vada.graph import load_seed
from src.logic.iks_nn import hill_inference, floor_absence
from src.ontology.pramana import PRAMANA_SETS

if HAS_FASTAPI:
    app = FastAPI(title="IKS-Core API", version="1.0.0")

    @app.get("/health")
    def health():
        return {"ok": True}

    @app.get("/pramana")
    def pramana():
        return {k: sorted(v) for k, v in PRAMANA_SETS.items()}

    @app.get("/vada")
    def vada():
        g = load_seed()
        return {"nodes": g.nodes, "edges": g.edges}

    @app.get("/demo/hill")
    def hill():
        return hill_inference()

    @app.get("/demo/absence")
    def absence():
        return {"render": floor_absence()}

    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8000)
else:
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            g = load_seed()
            body = {"ok": True, "graph": g.summary(), "hill": hill_inference(),
                    "absence": floor_absence(),
                    "pramana": {k: sorted(v) for k, v in PRAMANA_SETS.items()},
                    "note": "install fastapi+uvicorn for full router; stdlib fallback active"}
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *a):
            pass

    if __name__ == "__main__":
        print("IKS-Core demo API (stdlib) on http://0.0.0.0:8000 — install fastapi for full API")
        HTTPServer(("0.0.0.0", 8000), H).serve_forever()

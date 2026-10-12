import json, sys
from pathlib import Path
p = Path(__file__).resolve().parents[1] / "schema" / "iks-schema.json"
schema = json.loads(p.read_text())
assert "definitions" in schema and "Text" in str(schema)
print("schema OK:", p)
for name in ("texts.json", "sutras.json", "vada_nodes.json", "vada_edges.json"):
    d = json.loads((Path(__file__).resolve().parents[1] / "data" / name).read_text(encoding="utf-8"))
    print(name, "records:", len(d))
